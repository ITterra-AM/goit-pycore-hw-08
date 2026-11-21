from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
class Birthday(Field):
    def __init__(self, value):
        try:
            value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
        
class Name(Field):
    def __init__(self, value):
        if value is None or not str(value).strip():
            raise ValueError("Required name")
        super().__init__(str(value).strip())

class Phone(Field):
     def __init__(self, value):
        value = str(value)
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Required phone number (10 numbers)")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def add_phone(self, phone, *args):
        phones = [Phone(number) for number in (phone, *args)]
        self.phones.extend(phones)


    def find_phone(self, phone):
        phone = str(phone)
        for existing_phone in self.phones:
            if existing_phone.value == phone:
                return existing_phone
        return None


    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise ValueError("Phone is not found")
        self.phones.remove(found)


    def edit_phone(self, old_phone, new_phone):
        old_phone = str(old_phone)
        for index, existing_phone in enumerate(self.phones):
            if existing_phone.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return
        raise ValueError("Phone is not found")


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(str(name))

    def delete(self, name):
        self.data.pop(str(name), None)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value
            try:
                birthday_this_year = birthday.replace(year=today.year)
            except ValueError:
                birthday_this_year = birthday.replace(year=today.year, month=3, day=1)

            if birthday_this_year < today:
                try:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                except ValueError:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1, month=3, day=1)

            days_until_birthday = (birthday_this_year - today).days

            if days_until_birthday <= 7:
                congrat_date = birthday_this_year

                if congrat_date.weekday() == 5:
                    congrat_date += timedelta(days=2)
                elif congrat_date.weekday() == 6:
                    congrat_date += timedelta(days=1)

                result.append({'name': record.name.value, 'congratulation_date': congrat_date.strftime('%d.%m.%Y')})

        return result


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Please write a valid name and phone number."
        except IndexError:
            return "Please write arguments for the command."
    return wrapper

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_number, new_number = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_number, new_number)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return f"{name}: {', '.join(p.value for p in record.phones)}"    
    

@input_error
def show_all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts found."
    contact_list = "\n".join(str(record) for record in book.data.values())
    return f"All contacts:\n{contact_list}"

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday is None:
        return "Birthday not found."
    return f"{name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book: AddressBook):
    result = book.get_upcoming_birthdays()
    if not result:
        return "On next week not have birthday"
    return "\n".join(f"{p['name']}: {p['congratulation_date']}" for p in result)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "help":
            print("Available commands:")
            print("  hello - Greet the bot")
            print("  add <name> <phone> - Add a new contact")
            print("  change <name> <phone> - Change an existing contact's phone number")
            print("  phone <name> - Show the phone number of a contact")
            print("  all - Show all contacts")
            print("  add-birthday <name> <birthday> - add a new birthday date")
            print("  show-birthday <name> - show the birthday date of a contact")
            print("  birthdays - show the birthdays on next week of a contact")
            print("  help - Show available commands")
            print("  close/exit - Exit the program")
        else:
            print("Invalid command.")
    save_data(book)
if __name__ == "__main__":
    main()