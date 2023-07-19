from flask import Flask, jsonify

app = Flask(__name__)

# Fake leads data
leads_data = [
    {
        'Date de Soumission': 'July 18, 2023',
        'Nom de la Campagne': 'NEW',
        'Avez-vous travaillé': 'NEW',
        'Nom': 'NEW',
        'Prénom': 'NEW',
        'Téléphone': '0609254539',
        'Email': 'w.cohen@reselform.fr',
        'Qualification': 'nrp1',
        'Comments': 'NEW',
        'Assign to': 'Jatin',
        'Action': '',
    },
    {
        'Date de Soumission': 'July 18, 2023',
        'Nom de la Campagne': 'New lead',
        'Avez-vous travaillé': 'with me',
        'Nom': 'Jatin',
        'Prénom': 'Kant',
        'Téléphone': '076187876',
        'Email': 'jatin@gmail.com',
        'Qualification': 'pas_de_budget',
        'Comments': 'none',
        'Assign to': 'saurav singh',
        'Action': '',
    },
    {
        'Date de Soumission': 'July 19, 2023',
        'Nom de la Campagne': 'reselform selling partner',
        'Avez-vous travaillé': 'joo',
        'Nom': 'partner',
        'Prénom': 'reselform',
        'Téléphone': '0609254539',
        'Email': 'w.cohen@reselform.fr',
        'Qualification': 'nrp3',
        'Comments': '',
        'Assign to': 'Fatou nd',
        'Action': '',
    },
]

@app.route('/leads/', methods=['GET'])
def get_leads():
    return jsonify(leads_data)

if __name__ == '__main__':
    app.run(debug=True)
