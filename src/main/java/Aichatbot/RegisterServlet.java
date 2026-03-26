package Aichatbot;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@SuppressWarnings("serial")
@WebServlet("/register")
public class RegisterServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/plain");
        response.getWriter().println("Register Servlet Working ✅");
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        String username = request.getParameter("username");
        String password = request.getParameter("password");

        Connection con = null;
        PreparedStatement ps = null;

        try {

            // 🔥 Important for Java 23 + Tomcat
            Class.forName("com.mysql.cj.jdbc.Driver");

            con = DriverManager.getConnection(
            	    "jdbc:mysql://crossover.proxy.rlwy.net:46973/railway?useSSL=false&allowPublicKeyRetrieval=true",
            	    "root",
            	    "XHXMgkywywhyeNYKkIOBXlXzNXnTlmxo"
            	);

            ps = con.prepareStatement(
                    "INSERT INTO chatbot(username,password) VALUES (?,?)");

            ps.setString(1, username);
            ps.setString(2, password);

            ps.executeUpdate();

            out.print("{\"status\":\"success\"}");

        } catch (Exception e) {
            e.printStackTrace();
            out.print("{\"status\":\"error\",\"message\":\"" + e.getMessage() + "\"}");
        } finally {
            try {
                if (ps != null) ps.close();
                if (con != null) con.close();
            } catch (Exception ignored) {}
        }
    }
}
