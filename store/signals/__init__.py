# define custom signals
from django.contrib.auth import user_logged_in
from django.dispatch import Signal

# create a signal instance 
user_logged_in_signal = Signal()
order_created_signal = Signal()
