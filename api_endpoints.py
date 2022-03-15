import requests
from hashlib import sha512
import base64
import pytest
import os
import time

@pytest.fixture(autouse = True, scope="module")
def image():
    image_name = 'test_image_' + str(int(time.time()*1000))
    print(f"image: {image_name}")
    print("setup_module ", os.system(f"docker build --quiet -t {image_name} ."))

    yield image_name

    print("teardown_module ", os.system(f"docker rmi -f {image_name}"))

@pytest.fixture
def server_port(image):
    port = '8080'
    container_name = 'hashserver' + str(int(time.time()*1000))
    os.system(f"docker run --rm -d -p {port}:8888 --name {container_name} {image} /broken-hashserve/broken-hashserve_linux")
    time.sleep(1)

    yield port

    os.system(f"docker stop -t 0 {container_name}")

def test_check_sending_password_status_code_is_200(server_port):

    payload = {"password":"sunshine"}

    response = requests.post(f"http://localhost:{server_port}/hash", json=payload)

    assert response.status_code == 200
    response_body = response.json()

def test_checking_sending_password_returns_appropriate_job_id(server_port):

    payload = {"password":"angrymonkey"}

    response = requests.post("http://localhost:8080/hash", json=payload)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body == 1

def test_check_send_password_response_body_is_not_none(server_port):

    payload = {"password":"angrymonkey1"}

    response = requests.post("http://localhost:8080/hash", json=payload)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body is not None

def test_sending_empty_password_status_code_is_200(server_port):

    payload = {"password": ""}

    response = requests.post("http://localhost:8080/hash", json=payload)

    assert response.status_code == 200

def test_checking_empty_password_should_return_id(server_port):

    payload = {"password": ""}

    response = requests.post("http://localhost:8080/hash", json=payload)
    response_body = response.json()


    assert response.status_code == 200
    assert response_body == 1

def test_checking_one_character_password_should_return_the_id(server_port):

    payload = {"password": "d"}

    response = requests.post("http://localhost:8080/hash", json=payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == 1

def test_get_job_id_check_header_content_type_is_a_text(server_port):

    response =requests.get("http://localhost:8080/hash")

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'

def test_base64_encoded_password_is_returned_for_valid_id(server_port):
    password = 'angrymonkey'
    payload = {"password": password}

    response1 = requests.post("http://localhost:8080/hash", json=payload)
    assert response1.status_code == 200
    response2 = requests.get(f"http://localhost:8080/hash/{response1.text}")

    assert response2.status_code == 200
    assert response2.text == "NN0PAKtieayiTY8/Qd53AeMzHkbvZDdwYYiDnwtDdv/FIWvcy1sKCb7qi7Nu8Q8Cd/MqjQeyCI0pWKDGp74A1g=="

def test_check_returned_hash_corresponds_to_sha512_algorithm(server_port):
    password = 'sunday'
    payload = {"password": password}
    exp_answer = sha512(password.encode('utf-8')).digest()
    exp_answer = base64.b64encode(exp_answer)
    exp_answer = str(exp_answer, 'ascii')

    response1 = requests.post("http://localhost:8080/hash", json=payload)
    assert response1.status_code == 200
    response2 = requests.get(f"http://localhost:8080/hash/{response1.text}")
    assert response2.status_code == 200

    assert response2.text == exp_answer

def test_verify_that_encoded_password_is_not_returned_for_invalid_id(server_port):

    response = requests.get("http://localhost:8080/hash/131")

    assert response.status_code == 400

def test_check_same_password_returns_the_same_hash(server_port):
    password = 'nature'
    payload = {"password": password}

    response1 = requests.post("http://localhost:8080/hash", json=payload)
    assert response1.status_code == 200
    response2 = requests.get(f"http://localhost:8080/hash/{response1.text}")
    assert response2.status_code == 200
    first_password_hash = response2.text

    password2 = 'nature'
    payload2 = {"password": password2}

    response3 = requests.post("http://localhost:8080/hash", json=payload2)
    assert response3.status_code == 200
    response4 = requests.get(f"http://localhost:8080/hash/{response3.text}")
    second_password_hash = response4.text

    assert first_password_hash == second_password_hash

def test_check_different_passwords_do_not_have_the_same_hash(server_port):
    password = 'nature'
    payload = {"password": password}

    response1 = requests.post("http://localhost:8080/hash", json=payload)
    assert response1.status_code == 200
    response2 = requests.get(f"http://localhost:8080/hash/{response1.text}")

    assert response2.status_code == 200
    first_password_hash = response2.text

    password2 = 'planet'
    payload2 = {"password": password2}

    response3 = requests.post("http://localhost:8080/hash", json=payload2)
    assert response3.status_code == 200
    response4 = requests.get(f"http://localhost:8080/hash/{response3.text}")
    second_password_hash = response4.text

    assert first_password_hash != second_password_hash

def test_get_stats_of_all_jobs_returns_total_requests_in_response(server_port):
    response = requests.get("http://localhost:8080/stats")

    response_body = response.json()

    assert "TotalRequests" in response_body

def test_get_stats_of_all_jobs_returns_number_of_created_jobs(server_port):
    response = requests.get("http://localhost:8080/stats")

    response_body = response.json()

    assert type(response_body['TotalRequests']) is int

def test_get_stats_of_all_jobs_returns_average_time_of_hash_in_response(server_port):
    response = requests.get("http://localhost:8080/stats")

    response_body = response.json()

    assert "AverageTime" in response_body

def test_get_stats_of_all_jobs_returns_average_time_in_integers(server_port):
    response = requests.get("http://localhost:8080/stats")

    response_body= response.json()

    assert type(response_body["AverageTime"]) is int

def test_get_stats_of_all_jobs_shows_correct_number_of_jobs(server_port):
    payload1 = {"password": "sunset"}
    response1 = requests.post("http://localhost:8080/hash", json=payload1)
    assert response1.status_code == 200

    payload2 = {"password": "life"}
    response2 = requests.post("http://localhost:8080/hash", json=payload2)
    assert response2.status_code == 200

    payload3 = {"password": "ocean"}
    response3 = requests.post("http://localhost:8080/hash", json=payload3)
    assert response3.status_code == 200


    total_requests = requests.get("http://localhost:8080/stats")

    assert total_requests.json()['TotalRequests'] == 3

def test_get_stats_of_all_jobs_should_not_accept_any_input_data(server_port):
    response = requests.get("http://localhost:8080/stats/5")

    assert response.status_code == 404

def test_check_multiple_passwords_can_be_sent_simoultaneously_to_the_server(server_port):
    payload1 = {"password": "sunset"}
    payload2 = {"password": "life"}
    payload3 = {"password": "ocean"}

    response1 = requests.post("http://localhost:8080/hash", json=payload1)
    response2 = requests.post("http://localhost:8080/hash", json=payload2)
    response3 = requests.post("http://localhost:8080/hash", json=payload3)


    assert response2.status_code == 200
    assert response1.status_code == 200
    assert response3.status_code == 200

def test_check_post_returns_job_id_immidaitly_(server_port):
    payload = {"password": "sunday"}

    response = requests.post("http://localhost:8080/hash", json=payload, timeout=1)
    assert response.status_code == 200


# Bug report created: post with password send returns the job id after waiting 5 sec.

def test_shutting_down_should_allow_any_in_flight_password_hashing_to_complete(server_port):
    payload1 = {"password": "california"}
    payload2 = {"password": "newyork"}

    response1 = requests.post("http://localhost:8080/hash", json=payload1)
    response2 = requests.post("http://localhost:8080/hash", json=payload2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    shutdown = requests.post("http://localhost:8080/hash", data = 'shutdown')

    assert shutdown.status_code == 200


def test_shutting_down_should_return_empty_response(server_port):
    payload1 = {"password": "chicago"}

    response = requests.post("http://localhost:8080/hash", json=payload1)
    assert response.status_code == 200

    shutdown = requests.post("http://localhost:8080/hash", data = 'shutdown')

    assert shutdown.status_code == 200
    assert shutdown.text == ""



