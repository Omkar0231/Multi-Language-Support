# To run the project

#### Create a virtual environment and activate it.
```
pip install -r requirements.txt
```
#### Run the migrate command.
```
python manage.py migrate
```
#### Create a Super user.
```
python manage.py createsuperuser
```
#### Run the server
```
python manage.py runserver
```


# Answers for the Given Questions.

## Q1
#### When Django’s LANGUAGES parameter is updated (e.g. one more language is added/removed), a corresponding field must be added/removed automatically.

### Answer:
##### Yes. I have implemented the code in teh same way. When the parameter in the admin panel is updated the fields in the django admin will eb updated.

## Q2
#### Default language field must be required, it must not be allowed for a user to save any model without default language value specified.

### Answer:
##### Yes. I have made a choice field for the default language for each field that uses the Multi Language JSON field (This is the field which I have created.)

## Q3
#### Cover your code with a few unit tests.

### Answer:
##### Yes. I have written few Test cases for creating and getting the Object through django admin API.

## Q4
#### Implementation should be as flexible as possible – try to avoid any “hardcoded” features. What happens if you want to add one more model to your project, will you be able to easily add translation feature to a new field?

### Answer:
##### Yes. I have followed all the rules that you have mentioned. I have written the code in the way that we can create any number of models, new fields with the custom Multi Language JSON Field, the admin panel will work as expected.

## Q5
#### Try to reuse Django default API as much as possible.

### Answer:
##### Yes. I have used it.

# My Views
### Pros:
##### 1. This method solves the problem of migrating everytime we add a new language.
##### 2. It increases the readability of the data in the Admin Panel. We can also easily update the required field. 

### Cons
##### 1. There might be a case where the json data can be corrupted or changed by running custom queries.
##### 2. Querying on such fields is not an easier task. For Example: Getting all the objet whose json_field has 'en' language null.

### My Personal view
##### * This method is very useful. Because we always doesn't want to query as the 2 point above in cons. Mostly this data is for the Front End Applications's to show the data. 
##### * This solves the problem of migrating the database everytime we add a new language.


## Time Spent : 10 - 11 hrs


