# Storefront_v2 (Django – Advanced Variation)

Developed an alternative version of storefront with more advanced features:

## Cart System
- Implemented session-based carts for anonymous users.  
- Used Django signals to automatically merge session carts with user carts upon login.  

## Authentication
- Built custom authentication using phone number + password instead of username/email.  
- Added phone number validation using **django-phonenumbers** library.  

## Caching
- Integrated **DRF-extensions** response caching with **Redis** for automatic cache invalidation on updates/deletes.  

## Favorites
- Implemented favorites system using Django’s **ContentType** framework, enabling generic relationships (supporting products, categories, or any model).  

## Background Tasks
- Scheduled automatic deletion of empty carts using **Celery worker & beat**, ensuring database cleanliness.  

## Dockerization
- Containerized the app with **Docker & Docker Compose**, orchestrating Django, Redis, Celery worker, Celery beat & Flower with a single command.  
