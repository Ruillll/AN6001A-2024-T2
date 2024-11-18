from flask import Flask
from flask import render_template,request

Homework1 = Flask(__name__)

@Homework1.route("/",methods=["GET","POST"])
def index():
    return(render_template("q&a.html"))


if __name__ == "__main__":
    Homework1.run()