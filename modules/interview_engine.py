def get_questions(role, level):

    questions = {

        "Python Developer": {
            "Beginner": [
                "What is Python?",
                "What are variables in Python?",
                "What is a list?",
                "What is a tuple?",
                "What is a function?"
            ],

            "Intermediate": [
                "What is the difference between a list and a tuple?",
                "What is list comprehension?",
                "Explain *args and **kwargs.",
                "What is exception handling?",
                "What are modules in Python?"
            ],

            "Advanced": [
                "Explain Python decorators.",
                "What are generators?",
                "Explain multithreading in Python.",
                "What is the GIL?",
                "Explain context managers."
            ]
        },

        "Java Developer": {
            "Beginner": [
                "What is Java?",
                "What is a class?",
                "What is an object?",
                "What is inheritance?",
                "What is polymorphism?"
            ],

            "Intermediate": [
                "What is inheritance?",
                "What is encapsulation?",
                "What is method overloading?",
                "What is method overriding?",
                "Explain interfaces."
            ],

            "Advanced": [
                "Explain JVM memory management.",
                "What is garbage collection?",
                "Explain Java streams.",
                "What are design patterns?",
                "What is concurrency in Java?"
            ]
        },

        "Data Analyst": {
            "Beginner": [
                "What is data analysis?",
                "What is Excel?",
                "What is a dataset?",
                "What is data cleaning?",
                "What is a KPI?"
            ],

            "Intermediate": [
                "What is data cleaning?",
                "What is EDA?",
                "What is SQL?",
                "What is a JOIN?",
                "What is normalization?"
            ],

            "Advanced": [
                "Explain supervised learning.",
                "Explain unsupervised learning.",
                "What is feature engineering?",
                "What is cross validation?",
                "What is overfitting?"
            ]
        },

        "Frontend Developer": {
            "Beginner": [
                "What is HTML?",
                "What is CSS?",
                "What is JavaScript?",
                "What is a div?",
                "What is a hyperlink?"
            ],

            "Intermediate": [
                "What is the DOM?",
                "What is event bubbling?",
                "What is local storage?",
                "What is responsive design?",
                "What is flexbox?"
            ],

            "Advanced": [
                "Explain virtual DOM.",
                "What are React hooks?",
                "What is state management?",
                "What is server-side rendering?",
                "What is code splitting?"
            ]
        }
    }

    return questions[role][level]