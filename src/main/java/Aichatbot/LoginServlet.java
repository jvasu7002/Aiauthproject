package Aichatbot;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@SuppressWarnings("serial")
@WebServlet("/login")
public class LoginServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/plain");
        response.getWriter().println("Login Servlet Working ✅");
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        String username = request.getParameter("username");
        String password = request.getParameter("password");

        Connection con = null;
        PreparedStatement ps = null;
        ResultSet rs = null;

        try {
            // ✅ Input validation
            if (username == null || password == null || username.isEmpty() || password.isEmpty()) {
                out.print("{\"status\":\"error\",\"message\":\"Username or Password cannot be empty\"}");
                return;
            }

            // ✅ Load driver
            Class.forName("com.mysql.cj.jdbc.Driver");

            // ✅ Railway DB connection
            con = DriverManager.getConnection(
                "jdbc:mysql://crossover.proxy.rlwy.net:46973/railway?useSSL=false&allowPublicKeyRetrieval=true",
                "root",
                "XHXMgkywywhyeNYKkIOBXlXzNXnTlmxo"
            );

            // ✅ Query
            ps = con.prepareStatement(
                "SELECT * FROM chatbot WHERE username=? AND password=?"
            );

            ps.setString(1, username);
            ps.setString(2, password);

            rs = ps.executeQuery();

            if (rs.next()) {
                out.print("{\"status\":\"success\"}");
            } else {
                out.print("{\"status\":\"fail\",\"message\":\"Invalid credentials\"}");
            }

        } catch (Exception e) {
            e.printStackTrace();

            out.print("{\"status\":\"error\",\"message\":\"" + e.getMessage().replace("\"", "'") + "\"}");
        } finally {
            try {
                if (rs != null) rs.close();
                if (ps != null) ps.close();
                if (con != null) con.close();
            } catch (Exception ignored) {}
        }
    }
}