document.addEventListener("DOMContentLoaded", () => {
  const reportForm = document.getElementById("reportForm");
  const message = document.getElementById("message");

  if (reportForm) {
    reportForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        category: document.getElementById("category").value,
        status: document.getElementById("status").value,
        location: document.getElementById("location").value,
      };

      try {
        const response = await fetch("http://localhost:5000/items", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        if (response.ok) {
          const data = await response.json();
          message.textContent = "✅ Item reported successfully!";
          message.style.color = "green";
          reportForm.reset();
        } else {
          message.textContent = "❌ Error reporting item.";
          message.style.color = "red";
        }
      } catch (error) {
        console.error("Error:", error);
        message.textContent = "⚠️ Server error.";
        message.style.color = "red";
      }
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  // Existing Report Form handler...

  // ✅ Load items if on items.html
  const itemsContainer = document.getElementById("itemsContainer");
  if (itemsContainer) {
    fetch("http://localhost:5000/items")
      .then((res) => res.json())
      .then((data) => {
        if (data.length === 0) {
          itemsContainer.innerHTML = "<p>No items reported yet.</p>";
          return;
        }

        let html = "";
        data.forEach((item) => {
          html += `
            <div class="item-card">
              <h3>${item.title}</h3>
              <p><strong>Description:</strong> ${item.description}</p>
              <p><strong>Category:</strong> ${item.category}</p>
              <p><strong>Status:</strong> ${item.status}</p>
              <p><strong>Location:</strong> ${item.location}</p>
            </div>
          `;
        });
        itemsContainer.innerHTML = html;
      })
      .catch((err) => {
        console.error("Error fetching items:", err);
        itemsContainer.innerHTML = "<p>⚠️ Could not load items.</p>";
      });
  }
});

