from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import CityCostModel
from utils import generate_pie_chart

app = Flask(__name__)

# Initialize model
model = CityCostModel()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_city = request.form.get('city')
        transport_mode = request.form.get('transport_mode')
        stay_duration = request.form.get('stay_duration')
        currency_mode = 'usd'

        total_cost_range, cost_breakdown = model.calculate_cost(selected_country, selected_city, transport_mode, stay_duration, currency_mode)

        if total_cost_range is not None:
            pie_chart_img = generate_pie_chart(cost_breakdown['Transport'], cost_breakdown['Hotel'], cost_breakdown['Food'])
            min_cost = total_cost_range[0]
            max_cost = total_cost_range[1]
            min_cost_usd = cost_breakdown.get('Min_USD', None)
            max_cost_usd = cost_breakdown.get('Max_USD', None)

            return redirect(url_for('results', 
                                    total_cost_min=min_cost, 
                                    total_cost_max=max_cost,
                                    total_cost_min_dollars=min_cost_usd, 
                                    total_cost_max_dollars=max_cost_usd, 
                                    transport_cost=cost_breakdown['Transport'], 
                                    hotel_cost=cost_breakdown['Hotel'], 
                                    food_cost=cost_breakdown['Food'], 
                                    pie_chart_img=pie_chart_img,
                                    selected_country=selected_country,
                                    selected_city=selected_city))
    
    countries = model.get_countries()
    return render_template('index.html', countries=countries)


@app.route('/results')
def results():
    total_cost_min = request.args.get('total_cost_min', type=float)
    total_cost_max = request.args.get('total_cost_max', type=float)
    total_cost_min_dollars = request.args.get('total_cost_min_dollars', type=float)
    total_cost_max_dollars = request.args.get('total_cost_max_dollars', type=float)
    transport_cost = request.args.get('transport_cost', type=float)
    hotel_cost = request.args.get('hotel_cost', type=float)
    food_cost = request.args.get('food_cost', type=float)
    pie_chart_img = request.args.get('pie_chart_img')

    return render_template('result.html', 
                           total_cost_min=total_cost_min, 
                           total_cost_max=total_cost_max,
                           total_cost_min_dollars=total_cost_min_dollars,
                           total_cost_max_dollars=total_cost_max_dollars,
                           transport_cost=transport_cost, 
                           hotel_cost=hotel_cost, 
                           food_cost=food_cost,
                           pie_chart_img=pie_chart_img)


@app.route('/get_cities/<country>')
def get_cities(country):
    cities = model.get_cities(country)
    return jsonify(cities)

if __name__ == '__main__':
    app.run(debug=True)