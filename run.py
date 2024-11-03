from app import create_app, config

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
