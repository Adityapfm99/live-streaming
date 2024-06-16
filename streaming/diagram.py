from graphviz import Digraph

# Create a class diagram
class_diagram = Digraph(comment='Class Diagram', graph_attr={'splines': 'ortho'})

# Define nodes for each class
class_diagram.node('User', '''
<<User>>
- id: Integer
- username: CharField
- email: CharField
- password: CharField
''')

class_diagram.node('Stream', '''
<<Stream>>
- id: Integer
- user_id: Integer
- title: CharField
- description: TextField
- is_active: BooleanField
- created_at: DateTimeField
- updated_at: DateTimeField
''')

class_diagram.node('Donation', '''
<<Donation>>
- id: Integer
- stream_id: Integer
- user_id: Integer
- amount: DecimalField
- is_confirmed: BooleanField
- created_at: DateTimeField
''')

class_diagram.node('Comment', '''
<<Comment>>
- id: Integer
- stream_id: Integer
- user_id: Integer
- content: TextField
- created_at: DateTimeField
''')

class_diagram.node('Payment', '''
<<Payment>>
- id: Integer
- user_id: Integer
- amount: DecimalField
- payment_method: CharField
- status: CharField
- transaction_id: CharField
- created_at: DateTimeField
''')

# Define relationships
class_diagram.edge('User', 'Stream', label='1-to-many')
class_diagram.edge('User', 'Donation', label='1-to-many')
class_diagram.edge('User', 'Comment', label='1-to-many')
class_diagram.edge('User', 'Payment', label='1-to-many')
class_diagram.edge('Stream', 'Donation', label='1-to-many')
class_diagram.edge('Stream', 'Comment', label='1-to-many')

# Render the class diagram
class_diagram_path = '/mnt/data/class_diagram'
class_diagram.render(class_diagram_path, format='png', cleanup=True)

class_diagram_path &#8203;:citation[oaicite:0]{index=0}&#8203;
