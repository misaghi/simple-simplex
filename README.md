# Simple Simplex! Simplex Algorithm Solver 🚀

Welcome to **Simple Simplex**, a Python-based implementation of the Simplex algorithm! This project is designed to solve Linear Programming (LP) problems using the **two-phase method**, offering a clear, educational, and effective solution for optimization enthusiasts. 🎯  

---

## 🔍 What is the Simplex Algorithm?

The **Simplex algorithm** is a widely used method to solve Linear Programming (LP) problems. These problems involve optimizing (maximizing or minimizing) a linear objective function subject to a set of linear constraints.  

### 🛠 The Two-Phase Method
The **two-phase method** is employed to solve LPs that require an initial feasible solution:  

1. **Phase 1**: Converts the LP into a form that ensures feasibility by introducing artificial variables and minimizing their sum.  
2. **Phase 2**: Solves the original LP once a feasible solution is found by optimizing the objective function.  

This method is particularly useful when starting from a non-basic feasible solution.  

---

## 📋 Input Format

Your LP problem must be defined in a specific format to use this solver:  

1. **Problem Type**: Specify whether to `minimize` or `maximize`.  
2. **Objective Function**: Separate the problem type from the objective function using a `:` (colon).  
3. **Constraints**: Write each constraint on a new line, preceded by the `s.t.` (subject to) keyword.  

> **Note**: The LP type (e.g., `MINIMIZE`, `maximize`, or a combination of both) can be written in either lowercase or uppercase.  

### Example Input
```plaintext
maximize: 3 * x + 5 * y  
s.t.:  
2 * x + y <= 10  
x + 3 * y <= 12  
x, y >= 0  
```

Simply place your LP definition in the `inputs` folder, and you're ready to solve it! ✅  

---

## 🔧 Technologies Used

This project is implemented in **pure Python** using the powerful [SymPy](https://www.sympy.org/en/index.html) library.  

### 📘 About SymPy
**SymPy** is a Python library for symbolic mathematics. It provides capabilities to handle algebraic expressions, calculus, matrices, and more, making it an excellent choice for solving optimization problems like LPs.  

---

## 🏃‍♂️ How to Run the Solver?

No installation is required! 🎉 Just follow these steps:  

1. Clone this repository.  
2. Write your LP problems in the `inputs` folder as text files.  
3. Run `main.py` to see the solution.  

```bash
python main.py
```

---

## 🤝 Contributing

If you encounter any issues, bugs, or have suggestions, I’d love to hear from you! Feel free to open an issue or submit a pull request. Your feedback helps make this project better! 🙌  

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).  

---

### 🌟 Thank You for Visiting!  

If you find this project helpful, don’t forget to give it a ⭐️ on GitHub! Your support means the world. 🌍
