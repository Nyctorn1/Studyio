from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return {
        "message": "دستیار مطالعه با موفقیت اجرا شد",
        "status": "فعال"
    }


@app.get("/about")
def about() :
    return {
        "message" : "این دستیار مطالعه برای یادگیری بهتر ساخته شده است." ,
        "status" : "فعال"
    }

if __name__ == "__main__":
    app.run(debug=True)