async function displayArticles(articles) {
    const articlesContainer = $(".articles");
    if (articles.length === 0) {
        articlesContainer.html("<p class='loading'>No new articles!</p>");
        return;
    }
    // Clear existing content
    articlesContainer.html("");

    // Create and append article elements
    articles.forEach(article => {
        const articleElement = document.createElement("p");
        articleElement.className = "article";
        articleElement.innerHTML = `
            <a class="article-title" href="${article.url}">${article.title}</a>
            <span class="article-date">
                ${article.date_published}
            </span>
        `;
        articlesContainer.append(articleElement);
    });
}

fetch("/articles")
    .then(response => response.json())
    .then(data => displayArticles(data))
    .catch(error => console.error("Error fetching articles:", error));