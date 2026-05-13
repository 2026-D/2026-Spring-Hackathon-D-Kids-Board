function getCookie(name) {
    const cookieValue = document.cookie
        .split("; ")
        .find((row) => row.startsWith(name + "="))
        ?.split("=")[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
}

// 編集ボタン押下を監視
document.addEventListener("click", async (event) => {
    const editButton = event.target.closest(".js-edit-prep");
    if (!editButton) return;

    event.preventDefault();

    const prepItemId = editButton.dataset.prepId;
    const apiUrl = editButton.dataset.apiUrl;
    if (!prepItemId || !apiUrl) return;

    const prepItemCard =
        editButton.closest("[data-prep-item-card]") ||
        document.querySelector(`[data-prep-item-card="${prepItemId}"]`);
    if (!prepItemCard) return;

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ prep_item_id: prepItemId }),
        });

        if (!response.ok) throw new Error("fetch failed");
        const data = await response.json();

        prepItemCard.innerHTML = `
          <input type="text" class="form-control" value="${data.name ?? ""}">
          <button type="button" class="btn btn-primary mt-2">保存</button>
        `;
    } catch (e) {
        console.error(e);
    }
});