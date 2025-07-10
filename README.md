## The App

This repository contains a Django project designed to fulfill a recruitment task focused on migrating user data between various models. 
The project utilizes Django's data migration capabilities, poetry for dependency management, and django-environ for secure configuration.

### **Task Description**

The primary goal of this challenge is to implement data migration script within a Django environment. 
The migration involves transferring records from Subscriber and SubscriberSMS models to a unified User model, 
while carefully handling existing Client records and various conflict resolution scenarios.

### **Project Setup and Running**
To get this project up and running locally, follow these steps:

1. Clone the repository:

```bash
git clone git@github.com:w-wajda/recruitment-app.git
```

2. Install dependencies with Poetry:

This project uses Poetry for dependency management. 
If you don't have it installed, follow the instructions on their website.

```bash
poetry install
```

3. Configure environment variables:

Copy the example environment file and fill in your SECRET_KEY.

```bash
cp .env.example .env
```

Open .env and set SECRET_KEY. Example: SECRET_KEY=your_very_secret_django_key

4. Run Django Migrations:

This will create the database schema 

```bash
python manage.py migrate
```

5. (Optional) Run Django development server:
If you want to interact with the Django shell or future admin interface:

```bash
python manage.py runserver
```


### **Running the data migration**

To execute the data migration for subscribers, run the following command:

```bash
python manage.py migrate_subcribers
```

To execute migration for GDPR consents, run the following command:

```bash
python manage.py migrate_gdpr_consents
```


### **Testing the Migration**

To ensure the migration works as expected, you can run the provided tests.

```bash
python manage.py test
```
