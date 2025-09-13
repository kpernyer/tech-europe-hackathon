# 🚀 Weaviate Business Document Demo

A beautiful, interactive demo showcasing Weaviate's document storage and semantic search capabilities.

## ✨ Demo Features

- **🎨 Beautiful Web Interface** - Modern, responsive design perfect for presentations
- **📊 Real-time Data Visualization** - Live document browser with rich formatting
- **🔍 Interactive Schema Explorer** - Visualize your data structure
- **🌐 Direct Weaviate Access** - Links to console and GraphQL playground
- **📱 Mobile-Friendly** - Responsive design works on all devices

## 🎯 Quick Start

### Option 1: One-Click Demo
```bash
python3 run_demo.py
```
This will:
- Check and start Weaviate if needed
- Open the demo in your browser
- Show all available endpoints

### Option 2: Manual Steps
```bash
# 1. Start Weaviate
docker-compose up -d

# 2. Run the step-by-step demo
python3 step1_connect.py    # Test connection
python3 step2_schema.py     # Create schema
python3 step3_add_data.py   # Add sample documents

# 3. Start the demo server
python3 demo_server.py

# 4. Open demo
# Visit: http://localhost:3000/demo_frontend.html
```

## 🌐 Demo URLs

- **📊 Demo Frontend**: http://localhost:3000/demo_frontend.html
- **🏠 Weaviate Console**: http://localhost:8080/
- **📈 GraphQL Playground**: http://localhost:8080/v1/graphql
- **🔧 API Docs**: http://localhost:8080/v1/meta

## 📁 Demo Structure

```
weaviate-demo/
├── demo_frontend.html      # Beautiful web interface
├── demo_server.py         # CORS-enabled server
├── run_demo.py           # One-click launcher
├── step1_connect.py      # Connection test
├── step2_schema.py       # Schema creation
├── step3_add_data.py     # Sample data insertion
├── visualize.py          # Terminal visualization
├── docker-compose.yml    # Weaviate configuration
└── requirements.txt      # Python dependencies
```

## 🎭 Perfect for Demos

This setup is ideal for:
- **📽️ Presentations** - Beautiful visual interface
- **🏫 Teaching** - Step-by-step progression  
- **🧪 Experimentation** - Easy to modify and extend
- **💼 Business demos** - Professional appearance
- **🔬 Development** - Full API access

## 🎨 Demo Screenshots

The frontend includes:
- Modern glass-morphism design
- Animated document cards
- Real-time status indicators
- Interactive schema visualization
- Direct links to Weaviate tools

## 🛠️ Customization

To add your own documents:
1. Modify `step3_add_data.py` with your data
2. Adjust the schema in `step2_schema.py` if needed
3. Update the frontend styling in `demo_frontend.html`

## 🐛 Troubleshooting

**Demo not loading?**
- Check Weaviate is running: `docker ps`
- Verify ports 8080 and 3000 are free
- Run `python3 step1_connect.py` to test connection

**No documents showing?**
- Run `python3 step3_add_data.py` to add sample data
- Check the console for errors
- Try refreshing the demo page

## 🎉 Next Steps

After the demo, explore:
- Adding semantic search with embeddings
- Implementing vector similarity queries
- Building custom GraphQL queries
- Integrating with your own applications