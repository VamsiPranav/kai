from flask import Flask, request, jsonify
from flask_cors import CORS
from main import app as langgraph_app
import json
import re



from langgraph_source_scripts.average_scores_calculator import averges_cal
from langgraph_source_scripts.past15daysales import gen_historic_sales
app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')

    # Process the question using your LangGraph app
    config = {"configurable": {"thread_id": "1"}}
    result = langgraph_app.invoke({"question": question}, config)

    # Extract the final generation from the result
    final_generation = result['generation']

    json_match = re.search(r'```json\n(.*?)```', final_generation, re.DOTALL)

    if json_match:
        json_str = json_match.group(1)
        try:
            graph_data = json.loads(json_str)
            final_generation = re.sub(r'```json\n.*?```', '', final_generation, flags=re.DOTALL).strip()

            return jsonify({
                "response": final_generation,
                "graph_data": graph_data
            })
        except json.JSONDecodeError:
            print("Error decoding JSON data")

    return jsonify({"response": final_generation})

    # return jsonify({"response": final_generation})

@app.route('/quick-insights', methods=['GET'])
def quick_insights():
    shelfLifeScore, viabilityScore, predictedRevenue = averges_cal()
    currentRevenue = gen_historic_sales()
    return jsonify({
        "shelfLifeScore": shelfLifeScore,
        "viabilityScore": viabilityScore,
        "currentRevenue": currentRevenue,
        "predictedRevenue": predictedRevenue
    })

@app.route('/generate-report', methods=['GET'])
def generate_report():
    generate_msg = "Give a complete overview of the store, present all analysis. And show relevant graphs or charts"
    config = {"configurable": {"thread_id": "4"}}
    result = langgraph_app.invoke({"question": generate_msg}, config)

    final_generation = result['generation']
    return jsonify({"response": final_generation})

if __name__ == '__main__':
    app.run(debug=True)