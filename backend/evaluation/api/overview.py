def data():
    return "No data available"


import requests

data = {
    "quiz_submissions": [{
        "attempt": 1,
        "fudge_points": 0.5,
        "questions": {
            "105749": {
                "score": 0.5,
                "comment": "Testing the api. Just ignore me"
            },
        }
    }]
}
res = requests.put("https://aalen.instructure.com/api/v1/courses/2395/quizzes/7542/submissions/48362",
                   json=data,
                   headers={
                       "Authorization": "Bearer 12612~9n9xH3CWw7TZ1H0TqzXqPIdMdBP884k9nAVdoarIeprM5fSpHH1rwQwUXzAmU0eW"}
                   )
print(res)
content = str(res.content, encoding="utf8")
print(content)
