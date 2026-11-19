from tests.conftest import criar_morador


def test_criar_morador_com_necessidade_vira_prioritario(client, corrego):
    morador = criar_morador(client, corrego["id"], tipo="CADEIRANTE", prioritario=False)
    assert morador["prioritario"] is True
    assert morador["tipoNecessidade"] == "CADEIRANTE"
    assert "criadoEm" in morador


def test_listar_prioritarios_por_corrego(client, corrego):
    criar_morador(client, corrego["id"], nome="Acamado Fictício", tipo="ACAMADO")
    criar_morador(client, corrego["id"], nome="Sem Necessidade")
    resp = client.get("/api/moradores/prioritarios", params={"corregoId": corrego["id"]})
    assert resp.status_code == 200
    assert [m["nome"] for m in resp.json()] == ["Acamado Fictício"]


def test_criar_morador_telefone_invalido_422(client, corrego):
    resp = client.post(
        "/api/moradores",
        json={"nome": "Teste", "telefone": "abc", "endereco": "Rua X, 1", "corregoId": corrego["id"]},
    )
    assert resp.status_code == 422


def test_criar_morador_tipo_invalido_422(client, corrego):
    resp = client.post(
        "/api/moradores",
        json={
            "nome": "Teste",
            "telefone": "11912345678",
            "endereco": "Rua X, 1",
            "corregoId": corrego["id"],
            "tipoNecessidade": "SUPERHEROI",
        },
    )
    assert resp.status_code == 422


def test_criar_morador_corrego_inexistente_404(client):
    resp = client.post(
        "/api/moradores",
        json={"nome": "Teste", "telefone": "11912345678", "endereco": "Rua X, 1", "corregoId": 999},
    )
    assert resp.status_code == 404


def test_obter_morador_inexistente_404(client):
    assert client.get("/api/moradores/999").status_code == 404


def test_atualizar_e_remover_morador(client, corrego):
    morador = criar_morador(client, corrego["id"])
    resp = client.put(f"/api/moradores/{morador['id']}", json={"tipoNecessidade": "IDOSO"})
    assert resp.status_code == 200
    assert resp.json()["prioritario"] is True
    assert client.delete(f"/api/moradores/{morador['id']}").status_code == 204
    assert client.get(f"/api/moradores/{morador['id']}").status_code == 404
