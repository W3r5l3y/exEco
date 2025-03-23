// Add event listener to the image input field
document.getElementById("post-image-add").addEventListener("click", function() {
    document.getElementById("imageInput").click();
});

// Display the selected image in the preview
document.getElementById("imageInput").addEventListener("change", function(event) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            let preview = document.getElementById("post-image-preview");
            preview.src = e.target.result;
            preview.removeAttribute("hidden");
            preview.style.display = "block";
            document.getElementById("post-image-add").setAttribute("hidden", true)
        };
        reader.readAsDataURL(file);
    }
});