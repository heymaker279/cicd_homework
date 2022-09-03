import pytest
from rest_framework.test import APIClient

from students.models import Student, Course
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory

    # Arrange-подготовка данных, достанем или положем в базу определенные записи
    # Act-тестируемый функционал, вызов того или иного метода
    # Assert-проверка того, что действие выполнено корректно


@pytest.mark.django_db
def test_get_first_course(client, courses_factory):
    course = courses_factory(name='Math')
    response = client.get(f'/api/v1/courses/{course.id}/')
    data = response.json()
    assert response.status_code == 200
    assert data['name'] == course.name


@pytest.mark.django_db
def test_get_courses_list(client, courses_factory):
    courses_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    data = response.json()
    assert type(data) == list
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_filtered_course_of_id(client, courses_factory):
    courses = courses_factory(_quantity=10)
    filters = {'id': courses[0].id}
    response = client.get('/api/v1/courses/', data=filters)
    data_list = response.json()
    assert response.status_code == 200
    assert len(data_list) == 1
    assert (data['id'] == courses[0].id for data in data_list)


@pytest.mark.django_db
def test_get_filtered_course_of_name(client, courses_factory):
    courses = courses_factory(_quantity=10)
    filters = {'name': courses[0].name}
    response = client.get('/api/v1/courses/', data=filters)
    data_list = response.json()
    assert response.status_code == 200
    assert len(data_list) == 1
    assert (data['name'] == courses[0].name for data in data_list)


@pytest.mark.django_db
def test_create_course(client):
    response = client.post('/api/v1/courses/', data={'name': 'Python development'}, format='json')
    data = client.get('/api/v1/courses/').json()
    assert response.status_code == 201
    assert len(data) == 1
    assert data[0]['name'] == 'Python development'


@pytest.mark.django_db
def test_update_course(client, courses_factory):
    courses = courses_factory(_quantity=10)
    course_id = courses[0].id
    response = client.patch(f'/api/v1/courses/{course_id}/', data={'name': 'Python development'}, format='json')
    data = response.json()
    assert response.status_code == 200
    assert data['name'] == 'Python development'


@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    courses = courses_factory(_quantity=10)
    course_id = courses[0].id
    response = client.delete(f'/api/v1/courses/{course_id}/')
    data = client.get('/api/v1/courses/').json()
    assert response.status_code == 204
    assert len(data) == 9
    assert client.get('/api/v1/courses/' + f'{course_id}/').status_code == 404
