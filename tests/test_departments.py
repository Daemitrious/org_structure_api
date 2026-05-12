def test_create_department_trims_name(client):
    response = client.post("/departments/", json={"name": "  Engineering  "})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering"
    assert data["parent_id"] is None


def test_cannot_create_empty_department_name(client):
    response = client.post("/departments/", json={"name": "   "})

    assert response.status_code == 422


def test_cannot_create_duplicate_department_name_in_same_parent(client):
    root = client.post("/departments/", json={"name": "Company"}).json()

    first_response = client.post(
        "/departments/",
        json={"name": "Backend", "parent_id": root["id"]},
    )
    second_response = client.post(
        "/departments/",
        json={"name": "Backend", "parent_id": root["id"]},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_can_create_same_department_name_in_different_parents(client):
    root_a = client.post("/departments/", json={"name": "Company A"}).json()
    root_b = client.post("/departments/", json={"name": "Company B"}).json()

    first_response = client.post(
        "/departments/",
        json={"name": "Backend", "parent_id": root_a["id"]},
    )
    second_response = client.post(
        "/departments/",
        json={"name": "Backend", "parent_id": root_b["id"]},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201


def test_create_employee_in_missing_department_returns_404(client):
    response = client.post(
        "/departments/999/employees/",
        json={"full_name": "Ivan Ivanov", "position": "Backend Developer"},
    )

    assert response.status_code == 404


def test_cannot_create_employee_with_empty_position(client):
    department = client.post("/departments/", json={"name": "Engineering"}).json()

    response = client.post(
        f"/departments/{department['id']}/employees/",
        json={"full_name": "Ivan Ivanov", "position": "   "},
    )

    assert response.status_code == 422


def test_get_department_tree_respects_depth(client):
    root = client.post("/departments/", json={"name": "Company"}).json()
    child = client.post(
        "/departments/",
        json={"name": "Engineering", "parent_id": root["id"]},
    ).json()
    client.post(
        "/departments/",
        json={"name": "Backend", "parent_id": child["id"]},
    )

    response = client.get(f"/departments/{root['id']}?depth=1")

    assert response.status_code == 200
    department = response.json()["department"]
    assert department["name"] == "Company"
    assert len(department["children"]) == 1
    assert department["children"][0]["name"] == "Engineering"
    assert department["children"][0]["children"] == []


def test_get_department_tree_can_exclude_employees(client):
    department = client.post("/departments/", json={"name": "Engineering"}).json()
    client.post(
        f"/departments/{department['id']}/employees/",
        json={"full_name": "Ivan Ivanov", "position": "Backend Developer"},
    )

    response = client.get(
        f"/departments/{department['id']}?include_employees=false",
    )

    assert response.status_code == 200
    assert response.json()["department"]["employees"] == []


def test_cannot_make_department_parent_of_itself(client):
    department = client.post("/departments/", json={"name": "Engineering"}).json()

    response = client.patch(
        f"/departments/{department['id']}",
        json={"parent_id": department["id"]},
    )

    assert response.status_code == 409


def test_cannot_move_department_inside_own_subtree(client):
    root = client.post("/departments/", json={"name": "Company"}).json()
    child = client.post(
        "/departments/",
        json={"name": "Engineering", "parent_id": root["id"]},
    ).json()

    response = client.patch(
        f"/departments/{root['id']}",
        json={"parent_id": child["id"]},
    )

    assert response.status_code == 409


def test_cascade_delete_department_deletes_children_and_employees(client):
    root = client.post("/departments/", json={"name": "Company"}).json()
    child = client.post(
        "/departments/",
        json={"name": "Engineering", "parent_id": root["id"]},
    ).json()
    client.post(
        f"/departments/{child['id']}/employees/",
        json={"full_name": "Ivan Ivanov", "position": "Backend Developer"},
    )

    delete_response = client.delete(f"/departments/{root['id']}?mode=cascade")
    get_child_response = client.get(f"/departments/{child['id']}")

    assert delete_response.status_code == 204
    assert get_child_response.status_code == 404


def test_reassign_delete_moves_employees_to_target_department(client):
    source = client.post("/departments/", json={"name": "Old Department"}).json()
    target = client.post("/departments/", json={"name": "New Department"}).json()
    client.post(
        f"/departments/{source['id']}/employees/",
        json={"full_name": "Ivan Ivanov", "position": "Backend Developer"},
    )

    delete_response = client.delete(
        f"/departments/{source['id']}?mode=reassign"
        f"&reassign_to_department_id={target['id']}",
    )
    target_response = client.get(f"/departments/{target['id']}")

    assert delete_response.status_code == 204
    employees = target_response.json()["department"]["employees"]
    assert len(employees) == 1
    assert employees[0]["full_name"] == "Ivan Ivanov"

#dimitry krushinski
def test_reassign_delete_for_department_with_children_returns_409(client):
    source = client.post("/departments/", json={"name": "Old Department"}).json()
    target = client.post("/departments/", json={"name": "New Department"}).json()
    client.post(
        "/departments/",
        json={"name": "Child", "parent_id": source["id"]},
    )

    response = client.delete(
        f"/departments/{source['id']}?mode=reassign"
        f"&reassign_to_department_id={target['id']}",
    )

    assert response.status_code == 409
