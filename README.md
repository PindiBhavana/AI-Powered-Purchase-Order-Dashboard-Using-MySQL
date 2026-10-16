# 📊 AI-Powered Purchase Order Dashboard using MySQL
Interactive procurement analytics dashboard built with Python, MySQL, Streamlit, and Plotly.

## 📌 Project Overview

The **AI-Powered Purchase Order Dashboard** is an interactive data analytics application developed using Python, MySQL, and Streamlit to monitor and analyze purchase order operations. It transforms procurement data into meaningful business insights through interactive visualizations, KPI metrics, and dynamic filters.

The dashboard helps users track purchase orders, analyze procurement spending, monitor vendor performance, evaluate departmental expenditure, and identify delivery status trends. It connects to a cloud-hosted MySQL database on Aiven, enabling the deployed Streamlit application to access data online.

## 🎯 Project Objectives

- Monitor purchase orders and their approval and delivery statuses.
- Analyze procurement spending across vendors and departments.
- Track delivery performance and identify overdue purchase orders.
- Provide interactive filters for exploring procurement data.
- Simplify purchasing analysis through an intuitive dashboard.

## 🛠️ Technologies Used

- **Python:** Data processing and application logic
- **MySQL:** Relational database management and SQL queries
- **Pandas:** Data manipulation and analysis
- **Streamlit:** Interactive dashboard development
- **Plotly:** Interactive charts and visualizations
- **Aiven:** Cloud-hosted MySQL database
- **Streamlit Community Cloud:** Application deployment
- **Python-dotenv and Streamlit Secrets:** Environment-based database configuration

## 📈 Key Features

- **KPI Metrics:** Summarizes key purchase order and spending indicators.
- **Procurement Spending Analysis:** Visualizes purchase order amounts and spending trends.
- **Vendor Analysis:** Examines purchasing activity across vendors.
- **Departmental Analysis:** Compares procurement activity and expenditure by department.
- **Purchase Order Status Tracking:** Analyzes orders by approval, ordering, receipt, and cancellation status.
- **Delivery Performance Monitoring:** Helps identify delayed and pending deliveries.
- **Interactive Filters:** Allows users to explore records based on available categories and dates.
- **Detailed Data Table:** Displays purchase order information for closer analysis.
- **CSV Export:** Enables users to download filtered data for further analysis.
- **Cloud Database Integration:** Connects the deployed application to an Aiven MySQL database.

## 🗄️ Database Design

The project uses a relational MySQL database named `defaultdb`, containing four tables:

| Table | Description |
|---|---|
| `purchase_orders` | Purchase order details, quantities, prices, dates, and statuses |
| `vendors` | Vendor information and categories |
| `departments` | Department details and annual budgets |
| `payments` | Payment amounts, invoice details, and payment statuses |

Primary keys, foreign keys, constraints, and relationships help maintain data integrity across the database.

## ⚙️ How It Works

1. Purchase order data is stored in a MySQL database.
2. The application connects to the cloud database using secure connection settings.
3. SQL queries retrieve purchase orders along with related vendor and department information.
4. Pandas processes the retrieved data for analysis.
5. Streamlit displays KPI metrics, charts, tables, and interactive filters.
6. Users explore procurement insights and export filtered results when required.

## 🚀 Deployment

The application is deployed using **Streamlit Community Cloud** and connects to a cloud-hosted MySQL database on **Aiven**. Database credentials are configured through Streamlit Secrets rather than hardcoded in the source code.

## 📂 Project Structure

```text
AI-Powered-Purchase-Order-Dashboard-using-MySQL/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── purchase_order_db.sql
└── dashboard.png
└── dashboard_filters.png
```

## ▶️ Run Locally

1. Clone the repository:

   ```bash
   git clone <YOUR_GITHUB_REPOSITORY_URL>
   cd AI-Powered-Purchase-Order-Dashboard-using-MySQL
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your database credentials in a local `.env` file:

   ```env
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=defaultdb
   ```

4. Start the application:

   ```bash
   streamlit run app.py
   ```

**Note:** A reachable MySQL database with the required tables and data must be available..

## 💡 Skills Demonstrated

- SQL querying and relational database design
- Data cleaning and manipulation using Pandas
- Exploratory data analysis and procurement analytics
- Interactive dashboard development
- Data visualization using Plotly
- Cloud database connectivity
- Application deployment and configuration management
- Translating operational data into business insights

## 👩‍💻 Conclusion

This project demonstrates how Python, SQL, and interactive visualizations can be combined to build a practical procurement analytics solution. It provides a centralized view of purchase order activity and helps users explore purchasing trends, vendor activity, departmental spending, and delivery performance through a cloud-deployed dashboard.
