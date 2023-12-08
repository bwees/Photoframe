var loadedData;

fetch("/api/images").then((response) => {
    response.json().then((data) => {
        loadedData = data;
        const imageList = document.getElementById("image-list")
        
        data.sort((a, b) => {
            return new Date(b.date) - new Date(a.date)
        })

        data.forEach((image) => {
            const htmlData = `
            <div class="col mb-4">
              <div class="card">
                <img src="/thumbnail/${image}" class="card-img-top" alt="...">
                <div class="card-body">
                    <input type="date" class="form-control" value="${image}" onchange="changeDate('${image}', this)"/>
                    <button onclick="deleteImage('${image}')" class="btn btn-danger mt-2">Delete</button>
                </div>
              </div>
            </div>
            `

            imageList.innerHTML += htmlData
        })
    })
})

function deleteImage(id) {
    fetch(`/api/images/${id}`, { method: "DELETE" }).then(() => {
        window.location.reload()
    })
}

function changeDate(id, input) {

    // check for date conflict with loadedData
    const dateCheck = new Date(input.value)
    const conflict = loadedData.find((image) => {
        return new Date(image) - dateCheck === 0
    })

    if (conflict) {
        alert("Date conflict on " + dateCheck.toISOString().split("T")[0] + ". Please choose another date.")
        input.value = id
        return
    }

    fetch(`/api/images/${id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ date: input.value }),
    }).then(() => {
        window.location.reload()
    })
}

// CROP IMAGE HANDLING

document.getElementById('upload').onchange = function () {
    if (this.files && this.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            
            var vanilla = new Croppie(document.getElementById("croparea"), {
                viewport: { width: 600/2, height: 488/2 },
                boundary: { width: 300, height: 300 },
                showZoomer: true,
                enableOrientation: true,
                enableExif: true
            });

            vanilla.bind({
                url: e.target.result,
                orientation: 4
            });

            document.getElementById("rotate").onclick = function () {
                vanilla.rotate(90);
            }

            document.getElementById("submit").onclick = async function () {
                //hide controls
                document.getElementById("crop-controls").hidden = true;

                // show spinner
                document.getElementById("upload-spinner").hidden = false;

                var formData = new FormData();
                var f = new File([await vanilla.result("blob")], "image.png", { type: "image/png" })

                formData.append("file", f);

                fetch("/uploader", {
                    method: "POST",
                    body: formData,
                }).then(() => {
                    window.location.reload()
                })
            }
            // show controls
            document.getElementById("crop-controls").hidden = false;

        }

        reader.readAsDataURL(this.files[0]);
    }
}