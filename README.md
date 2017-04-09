# Задача

Реализовать на python клиентскую библиотеку (модуль) для работы с REST API.
В качестве API можно взять любое REST API, например, https://jsonplaceholder.typicode.com
Ожидается что библиотека будет включать ориентировочно такие классы:

* ApiClient - Класс реализующий взаимодействие с REST API.
    * AbstractModel - абстрактный класс модели для работы с сущностью API (методы добавления, удаления, изменения и тп, сами методы реализовывать не нужно)
        * PostModel - модель для работы с публикациями (или любая другая сущность). Наследуется от AbstractModel.
    * CollectionClass/RecordSet - класс коллекции включающий в себя множество экземпляров моделей позволяющий делать фильтрацию и постраничную навигацию.

### Конспект/Сценарий использования библиотеки

```
api = ApiClient('https://jsonplaceholder.typicode.com/', 'user', 'pass')
blog_posts = api.PostModel.all() #получение всех записей
blog_posts = api.PostModel.filter(userId=1) #получение класса коллекции записей c фильтром userId = 1
blog_post = blog_posts.first() #первая запись из списка
blog_post = blog_posts.iter() #получение следующую запись из выборки
blog_post_items = api.PostModel.limit(10).page(2).items() #Получение конечного списка моделей с заданием постраничной навигации
```

Данный пример не является обязательным и конечным требованием.

### Требования

##### Общие требования

* Проект загрузить в систему контроля версии Github/Bitbucket.
* В проект необходимо включить инструкции по его сборке, установке, настройке и тестов, а также Makefile.

##### Дополнительные требования

* Реализация этих требований не обязательна, но будет плюсом:
* Необходимо обеспечить максимальное покрытие unit-тестами.
* Приложение должно обрабатывать ошибки возвращаемые API.
* Вынести библиотеку (модуль) в отдельный пакет, чтобы можно было устанавливать как зависимость через менеджер пакетов.
* Документирование кода, генерация документации например с использованием sphinx-doc.
* Соответствие кода PEP-8 и другим основным стандартам (Используя pylint, flake8 и тп).
