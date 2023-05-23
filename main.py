import pickle
from flask import Flask , request, jsonify

app = Flask(__name__)

with open("model_pipr.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return "hellpo from home page"

@app.route("/predict",methods=["POST"])
def predict():
    age = request.args.get("age")
    gender = request.args.get("gender")
    spo2 = request.args.get("spo2")
    pr = request.args.get("pr")
    nCov2 = request.args.get("nCoV2")
    data = [[float(age), float(gender), float(spo2), float(pr), float(nCov2)]]
    res = model.predict(data)[0]
    return jsonify({"oxy_flow":str(abs(res))})

if __name__ == '__main__':
    app.run(port=5000)
