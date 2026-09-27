BIEN = {"titre": "T2 centre", "ville": "Rennes", "prix": 200000, "surface": 50}


def test_creer_bien(client):
    r = client.post("/biens", json=BIEN)
    assert r.status_code == 201
    data = r.json()
    assert data["prix_m2"] == 4000
    assert data["statut"] == "a_visiter"


def test_prix_negatif_refuse(client):
    r = client.post("/biens", json={**BIEN, "prix": -5})
    assert r.status_code == 422


def test_modifier_statut(client):
    bien_id = client.post("/biens", json=BIEN).json()["id"]
    r = client.patch(f"/biens/{bien_id}", json={"statut": "visite"})
    assert r.status_code == 200
    assert r.json()["statut"] == "visite"
    assert r.json()["prix"] == 200000  # les autres champs n'ont pas bougé


def test_filtrer_par_statut(client):
    client.post("/biens", json=BIEN)
    client.post("/biens", json={**BIEN, "statut": "offre_faite"})
    r = client.get("/biens", params={"statut": "offre_faite"})
    assert len(r.json()) == 1


def test_supprimer_puis_404(client):
    bien_id = client.post("/biens", json=BIEN).json()["id"]
    assert client.delete(f"/biens/{bien_id}").status_code == 204
    assert client.get(f"/biens/{bien_id}").status_code == 404
