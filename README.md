# Fitness Supplements app

Web page with a fitness supplements catalog where the users can log-in to add new supplements or products.


# Tools used for this project

  - Python 3
  - HTML
  - CSS
  - Flask
  - Flask SQLAchemy
  - OAuth
  - Google Login
  - Facebook Login

# Installation

  1 [Install Python 3](https://classroom.udacity.com/nanodegrees/nd004/parts/fe81273e-394c-492a-892e-664bd3cc9d4a/modules/2a89d1b1-8ceb-4f42-8d3a-eb91701873e7/lessons/6ff26dd7-51d6-49b3-9f90-41377bff4564/concepts/f2bcda00-ca29-4357-8dd9-d82cfdbf452d)

  2 [Install Virtual Machine](https://classroom.udacity.com/nanodegrees/nd004/parts/51200cee-6bb3-4b55-b469-7d4dd9ad7765/modules/c57b57d4-29a8-4c5f-9bb8-5d53df3e48f4/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0)

  3 [Download Fitness_Supplement_App.zip](https://drive.google.com/drive/folders/1zsWLYaMqX8fQSzorZzMhezJTYf0UZh3A?usp=sharing)

# Usage

1 - Extract Fitness_Supplement_App.zip in your preferred folder. Open terminal and change your working directory to the folder where you uncompressed the Zip file using the "cd" command and execute the python file using "phyton3 app.py".

```v
$ vagrant up
$ vagrant ssh
$ cd "Uncompressed Fitness_Supplement_App.zip File Path"
$ phyton3 app.py
```

2 - Navigate through the different supplements and products using the pointer, a click over "Supplements" will display its products, a click over "Products" will display its information.

3- Login to add, edit and delete products, for supplements you can just add and edit. Once logged in the buttons will be available next to each supplement or product if it was created by the logged user.

# JSON API

To get the information as JSON files the following routes can be used:

Get all supplements:
/API/supplement/all/JSON

Get a specific supplement by id:
/API/supplement/<int:supplement_id>/JSON

Get a specific supplement by id:
/API/supplement/<int:supplement_id>/JSON

Get all supplement products by supplement id:
/API/supplement/<int:supplement_id>/product/all/JSON

Get a specific product by id:
/API/supplement/<int:supplement_id>/product/<int:product_id>/JSON

# Known Issues

The facebook login may not work for not facebook API administrator users since it requires a secure connection.

# License

**Free Software**