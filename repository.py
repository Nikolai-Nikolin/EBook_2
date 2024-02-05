from sqlalchemy import and_, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, joinedload
from connection import engine
from models import Books, Authors, Genres, Readers, BorrowedBooks, BooksGenres, BooksAuthors, Orders, OrderItems, Staff
from datetime import datetime

Session = sessionmaker(autoflush=False, bind=engine)


# ======================================= РАБОТАЕТ ==================================

# === УПРАВЛЕНИЕ КНИГАМИ ===

# Создание новой книги
def create_book(_book_data):
    with Session(autoflush=False, bind=engine) as db:
        book = Books(**_book_data)
        db.add(book)
        db.commit()
        if book:
            return "Книга создана!!!"
        else:
            return False


# Получение всего списка книг
def get_book_all():
    with Session(autoflush=False, bind=engine) as db:
        book_seek = db.query(Books).distinct().all()
        if book_seek:
            books_data = []
            for book in book_seek:
                book_data = {
                    'id': book.id,
                    'title': book.title,
                    'publication': book.publication,
                    'publication_date': book.publication_date,
                    'cover_image': book.cover_image,
                    'book_location': book.book_location,
                    'description': book.description,
                    'price': book.price,
                    'available_copies': book.available_copies,
                    'authors': [],
                    'genres': []
                }

                # Получение информации об авторах книги
                authors = db.query(Authors).join(BooksAuthors).filter(
                    BooksAuthors.book_id == book.id).all()
                for author in authors:
                    author_data = {
                        'id': author.id,
                        'author_name': author.author_name,
                        'description': author.description
                    }
                    book_data['authors'].append(author_data)

                # Получение информации о жанрах книги
                genres = db.query(Genres).join(BooksGenres).filter(
                    BooksGenres.book_id == book.id).all()
                for genre in genres:
                    genre_data = {
                        'id': genre.id,
                        'title_genre': genre.title_genre
                    }
                    book_data['genres'].append(genre_data)

                books_data.append(book_data)
            return books_data
        else:
            return None


# Поиск книги по id
def get_book(_book_id):
    with Session(autoflush=False, bind=engine) as db:
        book_seek = db.query(Books).filter_by(id=_book_id).first()
        if book_seek:
            book_data = {
                'id': book_seek.id,
                'title': book_seek.title,
                'publication': book_seek.publication,
                'publication_date': book_seek.publication_date,
                'cover_image': book_seek.cover_image,
                'book_location': book_seek.book_location,
                'description': book_seek.description,
                'price': book_seek.price,
                'available_copies': book_seek.available_copies
            }
            return book_data
        else:
            return None


# Изменение книги
def update_book(_book, book_id, _updated_data):
    with Session(autoflush=False, bind=engine) as db:
        db.query(Books).filter(Books.id == book_id).update(_updated_data)
        db.commit()
        updated_book = db.query(Books).get(book_id)
        serialized_book = {
            'id': updated_book.id,
            'title': updated_book.title,
            'publication': updated_book.publication,
            'publication_date': updated_book.publication_date.isoformat(),
            'cover_image': updated_book.cover_image,
            'book_location': updated_book.book_location,
            'description': updated_book.description,
            'price': updated_book.price,
            'available_copies': updated_book.available_copies
        }
        return serialized_book


# Удаление книги
def delete_book(_book_id):
    with Session(autoflush=False, bind=engine) as db:
        book_to_delete = db.query(Books).filter_by(id=_book_id).first()
        if book_to_delete:
            db.delete(book_to_delete)
            db.commit()
            return True
        else:
            return False


# Поиск автора по id
def get_author_found(author_id):
    with Session(autoflush=False, bind=engine) as db:
        author = db.query(Authors).get(author_id)
        if author:
            return author.id
        else:
            return None


# Добавить автора для книги
def add_author_to_book(_book_id, _author_id):
    with Session(autoflush=False, bind=engine) as db:
        book = db.query(Books).get(_book_id)
        author = db.query(Authors).get(_author_id)
        if book and author:
            book_author = BooksAuthors(book_id=_book_id, author_id=_author_id)
            db.add(book_author)
            db.commit()
            return True
        else:
            return False


# Удалить автора для книги
def remove_author_from_book(_book_id, _author_id):
    with Session(autoflush=False, bind=engine) as db:
        book_author = db.query(BooksAuthors).filter_by(
            book_id=_book_id, author_id=_author_id).first()
        print(book_author)
        if book_author:
            db.delete(book_author)
            db.commit()
            return True
        else:
            return False


# === УПРАВЛЕНИЕ АВТОРАМИ ===

# Создать автора
def create_author(author_data):
    existing_author = get_author_by_name(author_data['author_name'])
    if existing_author:
        return {'message': 'Автор с таким именем уже есть'}
    new_author = Authors(author_name=author_data['author_name'],
                         description=author_data.get('description'))
    with Session(autoflush=False, bind=engine) as db:
        try:
            db.add(new_author)
            db.commit()
            db.refresh(new_author)
            return {
                'id': new_author.id,
                'author_name': new_author.author_name,
                'description': new_author.description
            }
        except IntegrityError:
            db.rollback()
            return {'message': 'Не удалось создать автора из-за нарушения ограничений базы данных'}


# Получение автора по имени
# (эта функция без роута, т.к. она нужна только
# для проверки именни автора для функции create_author)
def get_author_by_name(author_name):
    with Session(autoflush=False, bind=engine) as db:
        return db.query(Authors).filter(Authors.author_name == author_name).first()


# Поиск автора по id
def get_author(author_id):
    with Session(autoflush=False, bind=engine) as db:
        author = db.query(Authors).filter(Authors.id == author_id).first()
        if author:
            return {
                'id': author.id,
                'author_name': author.author_name,
                'description': author.description
            }
        else:
            return None


# Получение списка всех авторов
def get_all_authors():
    with Session(autoflush=False, bind=engine) as db:
        authors = db.query(Authors).all()
        author_list = []
        for author in authors:
            author_info = {
                'id': author.id,
                'author_name': author.author_name,
                'description': author.description
            }
            author_list.append(author_info)
        return author_list


# Изменение автора
def update_author(author_id, updated_data):
    with Session(autoflush=False, bind=engine) as db:
        db.query(Authors).filter(Authors.id == author_id).update(updated_data)
        db.commit()
        updated_author = db.query(Authors).get(author_id)
        serialized_author = {
            'id': updated_author.id,
            'author_name': updated_author.author_name,
            'description': updated_author.description,
        }
        return serialized_author


# Удаление автора
def delete_author(author_id):
    with Session(autoflush=False, bind=engine) as db:
        author = db.query(Authors).filter(Authors.id == author_id).first()
        if author:
            db.delete(author)
            db.commit()
            return True
        else:
            return False


# === УПРАВЛЕНИЕ ЖАНРАМИ ===

# Создать жанр
def create_genre(genre_data):
    existing_genre = get_genre_by_title(genre_data['title_genre'])
    if existing_genre:
        return {'message': 'Жанр с таким названием уже есть'}
    new_genre = Genres(title_genre=genre_data['title_genre'])
    with Session(autoflush=False, bind=engine) as db:
        try:
            db.add(new_genre)
            db.commit()
            db.refresh(new_genre)
            return {
                'id': new_genre.id,
                'title_genre': new_genre.title_genre
            }
        except IntegrityError:
            db.rollback()
            return {'message': 'Не удалось создать жанр из-за нарушения ограничений базы данных'}


# Получение жанра по названию
# (эта функция без роута, т.к. она нужна только
# для проверки именни автора для функции create_genre)
def get_genre_by_title(title_genre):
    with Session(autoflush=False, bind=engine) as db:
        return db.query(Genres).filter(Genres.title_genre == title_genre).first()


# Поиск книги по id
def get_book_found(_book_id):
    with Session(autoflush=False, bind=engine) as db:
        book = db.query(Books).get(_book_id)
        return book


# Поиск жанра по id
def get_genre_found(_genre_id):
    with Session(autoflush=False, bind=engine) as db:
        genre = db.query(Genres).get(_genre_id)
        return genre


# Добавить жанр книги
def add_genre_to_book(_book_id, _genre_id):
    with Session(autoflush=False, bind=engine) as db:
        book = db.query(Books).get(_book_id)
        genre = db.query(Genres).get(_genre_id)
        if book and genre:
            book_genre = BooksGenres(book_id=_book_id, genre_id=_genre_id)
            db.add(book_genre)
            db.commit()
            return True
        else:
            return False


# Удалить жанр книги
def remove_genre_from_book(_book_id, _genre_id):
    with Session(autoflush=False, bind=engine) as db:
        book_genre = db.query(BooksGenres).filter_by(
            book_id=_book_id, genre_id=_genre_id).first()
        print(book_genre)
        if book_genre:
            db.delete(book_genre)
            db.commit()
            return True
        else:
            return False


# === УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ ===

# Создать читателя
def create_reader(_reader_data):
    with Session(autoflush=False, bind=engine) as db:
        reader = Readers(**_reader_data)
        db.add(reader)
        db.commit()
        if reader:
            return _reader_data
        else:
            return False


# Удалить читателя по id
def delete_reader_by_id(reader_id):
    with Session(autoflush=False, bind=engine) as db:
        reader = db.query(Readers).filter_by(id=reader_id).first()
        if reader:
            db.delete(reader)
            db.commit()
            return {"message": "Читатель успешно удален"}
        else:
            return {"error": "Читатель не найден"}


# Поиск читателя по id
def get_single_reader(_reader_id):
    with Session(autoflush=False, bind=engine) as db:
        reader = db.query(Readers).get(_reader_id)
        return reader


# Показать всех читателей
def get_reader(reader_id: int):
    with Session(autoflush=False, bind=engine) as db:
        return db.query(Readers).get(reader_id)


# Поиск активностей конкретного читателя
def get_reader_activity(_reader_id):
    with Session(autoflush=False, bind=engine) as db:
        reader = db.query(Readers).get(_reader_id)
        if not reader:
            return None, 404
        borrowed_books = (
            db.query(BorrowedBooks)
            .join(Books)
            .filter(BorrowedBooks.reader_id == _reader_id)
            .all()
        )
        activity = []
        for borrowed_book in borrowed_books:
            book = borrowed_book.book
            activity.append({
                "book": book,
                "date_borrowed": borrowed_book.date_borrowed,
                "date_returned": borrowed_book.date_returned,
                "is_returned": borrowed_book.is_returned
            })
        return activity, 200


# === УПРАВЛЕНИЕ ЗАКАЗАМИ ===

# Регистрация нового заказа на книги
def create_order(_book_ids):
    with Session(autoflush=False, bind=engine) as db:
        order = Orders(order_date=datetime.now(), status="Pending")
        print(order)
        db.add(order)
        db.commit()
        for book_id in _book_ids:
            book = db.query(Books).get(book_id)
            if book:
                order_item = OrderItems(
                    order_id=order.id, new_book_id=book_id, new_book_price=book.price, quantity=1)
                db.add(order_item)
        db.commit()


# Обновление статуса заказа
def update_order_status(_order_id, _status):
    with Session(autoflush=False, bind=engine) as db:
        order = db.query(Orders).get(_order_id)
        if order:
            order.status = _status
            db.commit()
            return True
        return False


# Обновляем количество книг в таблице books в случае "Completed, а также цены"
def update_book_quantity_and_price(_order_id):
    with Session(autoflush=False) as db:
        order_items = db.query(OrderItems).filter_by(order_id=_order_id).all()

        for item in order_items:
            book_id = item.new_book_id
            new_book_price = item.new_book_price
            quantity = item.quantity

            # Выполняем SQL-запрос для обновления количества книг в таблице books
            db.execute(update(Books).where(Books.id == book_id).values(
                available_copies=Books.available_copies + quantity, price=new_book_price))

        db.commit()
        return True


# Информация по конкретному заказу
def get_order_details(order_id):
    with Session(autoflush=False, bind=engine) as db:
        order = db.query(Orders).get(order_id)
        if order:
            order_details = {
                'order_id': order.id,
                'order_date': order.order_date,
                'status': order.status,
                'items': []
            }
            for item in order.order_items:
                book = db.query(Books).get(item.new_book_id)
                item_details = {
                    'book_id': book.id,
                    'book_title': book.title,
                    'book_price': item.new_book_price,
                    'quantity': item.quantity
                }
                order_details['items'].append(item_details)
            return order_details
        return None


# === УПРАВЛЕНИЕ ПЕРСОНАЛОМ ===

# Регистрация пользователя
def add_staff(staff):
    try:
        with Session(autoflush=False, bind=engine) as db:
            db.add(staff)
            db.commit()
    except SQLAlchemyError as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return f"Error creating user: {e}"


# Поиск авторизованного сотрудника
def get_staff(name, password):
    try:
        with Session(autoflush=False, bind=engine) as db:
            staff = db.query(Staff).filter(and_(Staff.name == name,
                                                Staff.password == password)).first()
        return staff
    except SQLAlchemyError as e:
        print(f"Error getting user: {e}")
        return None


# Ищем сотрудника по его роли (необходимо для роута авторизации)
def get_staff_role(staff_id):
    with Session(autoflush=False, bind=engine) as db:
        staff = db.query(Staff).filter_by(id=staff_id).first()
        if staff:
            return staff.role
        else:
            return None


# Поиск сотрудника по id
# def get_staff(_id):
#     with Session(autoflush=False, bind=engine) as db:
#         staff = db.query(Staff).filter_by(id=_id).first()
#         if staff:
#             staff_by_id = {
#                 'id': staff.id,
#                 'name': staff.name,
#                 'password': staff.password,
#                 'role': staff.role,
#                 'access_level': staff.access_level,
#                 'is_deleted': staff.is_deleted
#             }
#             return staff_by_id
#         else:
#             return False


# Просмотр всех сотрудников
def get_staff_all():
    with Session(autoflush=False, bind=engine) as db:
        staff_seek = db.query(Staff).all()
        if staff_seek:
            list_staff_data = []
            for staff in staff_seek:
                staff_data = {
                    'id': staff.id,
                    'name': staff.name,
                    'password': staff.password,
                    'role': staff.role,
                    'access_level': staff.access_level,
                    'is_deleted': staff.is_deleted
                }
                list_staff_data.append(staff_data)
            return list_staff_data
        else:
            return None


# Обновить роль для сотрудника
def update_staff_new_role(_id, _new_role):
    with Session(autoflush=False, bind=engine) as db:
        staff = db.query(Staff).filter_by(id=_id).first()
        if staff:
            staff.role = _new_role
            db.commit()
            return True
        return False


# Обновить уровень допуска для сотрудника
def update_staff_new_access_level(_id):
    with Session(autoflush=False, bind=engine) as db:
        staff = db.query(Staff).filter_by(id=_id).first()
        if staff:
            staff.access_level += 1
            db.commit()
            return True
        return False


# Удалить сотрудника (soft-delete)
def delete_staff(_id):
    with Session(autoflush=False, bind=engine) as db:
        staff = db.query(Staff).filter_by(id=_id).first()
        if staff:
            staff.is_deleted = True
            db.commit()
            return {"message": "Работник успешно удален"}
        else:
            return {"error": "Работник не найден"}
