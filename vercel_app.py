from app import create_app

app = create_app()

# Para Vercel Serverless Functions
if __name__ == '__main__':
    app.run(debug=True)