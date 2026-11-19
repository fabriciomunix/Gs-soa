from tests.conftest import criar_morador


def test_leitura_normal_nao_gera_alerta(client, sensor, corrego):
    resp = client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 40, "chuvaMmHora": 2})
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nivelRisco"] == "NORMAL"
    assert body["alerta"] is None
    assert body["moradoresPrioritarios"] == []
    assert client.get("/api/alertas").json() == []


def test_leitura_critica_cria_alerta_e_retorna_prioritarios(client, sensor, corrego):
    idoso = criar_morador(client, corrego["id"], nome="Idoso Fictício", tipo="IDOSO")
    criar_morador(client, corrego["id"], nome="Vizinho Fictício")

    resp = client.post(
        "/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 190, "chuvaMmHora": 60}
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nivelRisco"] == "CRITICO"
    assert body["leitura"]["nivelAguaCm"] == 190
    assert body["alerta"]["nivelRisco"] == "CRITICO"
    assert body["alerta"]["ativo"] is True
    assert body["alerta"]["corregoId"] == corrego["id"]
    assert [m["id"] for m in body["moradoresPrioritarios"]] == [idoso["id"]]

    ativos = client.get("/api/alertas", params={"ativos": "true", "corregoId": corrego["id"]}).json()
    assert len(ativos) == 1


def test_leitura_alerta_gera_alerta(client, sensor):
    body = client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 125}).json()
    assert body["nivelRisco"] == "ALERTA"
    assert body["alerta"] is not None


def test_leitura_sensor_inexistente_404(client):
    resp = client.post("/api/leituras", json={"sensorId": 999, "nivelAguaCm": 10})
    assert resp.status_code == 404


def test_leitura_nivel_negativo_422(client, sensor):
    resp = client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": -5})
    assert resp.status_code == 422


def test_listar_leituras_por_corrego_com_limite(client, sensor, corrego):
    for nivel in (10, 20, 30):
        client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": nivel})
    resp = client.get("/api/leituras", params={"corregoId": corrego["id"], "limite": 2})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_encerrar_alerta(client, sensor):
    alerta = client.post("/api/leituras", json={"sensorId": sensor["id"], "nivelAguaCm": 200}).json()["alerta"]
    resp = client.patch(f"/api/alertas/{alerta['id']}/encerrar")
    assert resp.status_code == 200
    assert resp.json()["ativo"] is False
    assert client.get("/api/alertas", params={"ativos": "true"}).json() == []
    assert client.patch(f"/api/alertas/{alerta['id']}/encerrar").status_code == 409


def test_encerrar_alerta_inexistente_404(client):
    assert client.patch("/api/alertas/999/encerrar").status_code == 404
