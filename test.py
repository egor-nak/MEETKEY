from requests import get, post, delete

# print(post('http://localhost:5000/api/comments').json())
#
# print(post('http://localhost:5000/api/news',
#            json={'title': 'Заголовок'}).json())
print(post('http://localhost:5000/api/login',
           json={'password': '12345678', 'email': 'egor.nak@bk.ru'}).json())
print(delete('http://localhost:5000/api/comments/3').json())
# print(delete('http://localhost:5000/api/news/999').json())
