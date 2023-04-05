import plotly.graph_objs as go
from plotly.subplots import make_subplots
import random
import string
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from word_list import word_list



def generate_hidden_word(word_length):
    all_words = word_list()
    valid_words = [word for word in all_words if len(word) == word_length]
    return random.choice(valid_words)

def generate_wordle(hidden_word, num_rows):
    fig = make_subplots(rows=num_rows, cols=word_length, specs=[[{'type': 'domain'}]*word_length]*num_rows)
    for row in range(1, num_rows+1):
        for col in range(1, word_length+1):
            fig.add_trace(go.Table(header=dict(values=['']), cells=dict(values=[''])), row=row, col=col)
    fig.update_layout(height=800, width=800)
    return fig
word_length = 5
num_rows = 6
hidden_word = generate_hidden_word(word_length)


app = dash.Dash(__name__)

wordle = generate_wordle(hidden_word,num_rows)
#print(hidden_word)
app.layout = html.Div([
    html.H1('WORDLE',style ={'color':'pink','font-size':'90px'}),
    html.Div([
        dcc.Dropdown(
            id='word-length',
            options=[{'label': f'{i}-letter word', 'value': i} for i in range(2, 8)],
            value=5,
            style={'width': '100%'}
        ),
        dcc.Dropdown(
            id='num-guesses',
            options=[{'label': f'{i} guesses', 'value': i} for i in range(4, 9)],
            value=6,
            style={'width': '100%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin': 'auto','padding-bottom':'20px'}), # add margin: auto style to parent html.Div element
    html.Div([
        dcc.Input(id='input', type='text', value='', style={'width': '25%','height':'110px','font-size':'50px','margin-right':'20px'}), # add width: 50% style to dcc.Input element
        html.Button('Submit', id='submit-button', n_clicks=0,style = {'width':'110px','height':'110px'}),
        html.Button('Refresh', id='refresh-button', n_clicks=0,style = {'width':'110px','height':'110px'})
    ], style={'display': 'flex','justify-content':'center'}),
    html.Div([
        dcc.Graph(id='wordle', figure=wordle, style={'margin': 'auto'})
    ], style={'display': 'flex'}),
    html.Div('Game Over', id='game-over', style={'display': 'none', 'color': 'red', 'font-size': '36px'})
], style={'margin': 'auto', 'text-align': 'center'})


num_guesses = 0

@app.callback(
    [Output('wordle', 'figure'), Output('game-over', 'children'), Output('game-over', 'style')],
    Input('submit-button', 'n_clicks'),
    Input('refresh-button', 'n_clicks'),
    Input('word-length', 'value'),
    Input('num-guesses', 'value'),
    State('input', 'value'),
    State('game-over', 'children'),
    State('game-over', 'style')
)
def update_output(submit_clicks, refresh_clicks, word_length_value, num_guesses_value, value, game_over_text, game_over_style):
    global hidden_word
    global wordle
    global word_length
    global num_guesses
    
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    game_over_text = '' # default text for game-over element (empty)
    game_over_style = {'display': 'none'} # default style for game-over element (hidden)
    
    if button_id == 'submit-button':
        if num_guesses < num_guesses_value:
            # update wordle figure based on user's guess
            guess = value.lower()
            for i in range(word_length):
                if guess[i] == hidden_word[i]:
                    wordle['data'][num_guesses*word_length+i]['cells']['values'] = [[guess[i]]]
                    wordle['data'][num_guesses*word_length+i]['cells']['line_color'] = 'green'
                    wordle['data'][num_guesses*word_length+i]['cells']['fill_color'] = 'green'
                elif guess[i] in hidden_word:
                    wordle['data'][num_guesses*word_length+i]['cells']['values'] = [[guess[i]]]
                    wordle['data'][num_guesses*word_length+i]['cells']['line_color'] = 'yellow'
                    wordle['data'][num_guesses*word_length+i]['cells']['fill_color'] = 'yellow'
                else:
                    wordle['data'][num_guesses*word_length+i]['cells']['values'] = [[guess[i]]]
                    wordle['data'][num_guesses*word_length+i]['cells']['line_color'] = 'red'
                    wordle['data'][num_guesses*word_length+i]['cells']['fill_color'] = 'red'
            num_guesses += 1
            if num_guesses == num_guesses_value:
                game_over_text = f'Game Over. The hidden word was {hidden_word}'
                game_over_style = {'display': 'block', 'color': 'red', 'font-size': '36px'}
        else:
            game_over_text = f'Game Over. The hidden word was {hidden_word}'
            game_over_style = {'display': 'block', 'color': 'red', 'font-size': '36px'}
    elif button_id == 'refresh-button' or button_id == 'word-length' or button_id=='num-guesses':
        # reset wordle figure and generate new hidden word
        hidden_word = generate_hidden_word(word_length_value)
        word_length = word_length_value
        wordle = generate_wordle(hidden_word, num_guesses_value) # pass value of num-guesses dropdown as num_rows argument
        num_guesses = 0
        game_over_text = ''
        game_over_style = {'display': 'none'}
    print(hidden_word)
    return wordle, game_over_text, game_over_style
if __name__ == '__main__':
    app.run_server(debug=True)