from main import app

result = app.invoke({"question": "Which products have a high viability score?"})
print(result['generation'])