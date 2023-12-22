var loadedData;

fetch("/api/images").then((response) => {
    response.json().then((data) => {
        loadedData = data;

        const imageUpcomingList = document.getElementById("image-upcoming-list")
        const imagePastList = document.getElementById("image-past-list")

        var imageCounter = {
            past: 0,
            upcoming: 0
        }
        
        data.sort((a, b) => {
            return new Date(b.date) - new Date(a.date)
        })

        data.forEach((image) => {
            const completeHtmlData = `
            <div class="col mb-4">
              <div class="card">
                <img src="/thumbnail/${image.date}" class="card-img-top" alt="...">
                <div class="card-body">
                    <input type="date" class="form-control" value="${image.date}" onchange="changeDate('${image.date}', this)"/>
                    <button onclick="deleteImage('${image.date}')" class="btn btn-danger mt-2">Delete</button>
                </div>
              </div>
            </div>
            `

            const incompleteHtmlData = `
            <div class="col mb-4">
              <div class="card">
              <div style="text-align: center;">
                <div class="spinner-border mt-4" id="upload-spinner" role="status">
                </div>
                <p>Processing Image<p>
                <div class="card-body">
                    <input type="date" class="form-control" value="${image.date}" onchange="changeDate('${image.date}', this)"/>
                    <button onclick="deleteImage('${image.date}')" class="btn btn-danger mt-2">Delete</button>
                </div>
              </div>
            </div>
            `
            const htmlData = image.complete ? completeHtmlData : incompleteHtmlData

            //  if the image date is in the past, add to past list, otherwise add to upcoming list
            // only check if date is in the past, not if it is today
            if (new Date(image) < new Date(new Date().toISOString().split("T")[0])) {
                imagePastList.innerHTML += htmlData
                imageCounter.past++
            } else {
                imageUpcomingList.innerHTML += htmlData
                imageCounter.upcoming++
            }

        })

        if (imageCounter.past === 0) imagePastList.outerHTML = `<p class="text-center pt-2">No Images to Show</p>`
        if (imageCounter.upcoming === 0) imageUpcomingList.outerHTML = `<p class="text-center pt-2">No Images to Show</p>`

        document.getElementById("past-tab").innerHTML += ` (${imageCounter.past})`
        document.getElementById("upcoming-tab").innerHTML += ` (${imageCounter.upcoming})`
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
            
            var cropper = new Croppie(document.getElementById("croparea"), {
                viewport: { width: 600/2, height: 488/2 },
                boundary: { width: 300, height: 300 },
                showZoomer: true,
                enableOrientation: true,
                enableExif: true
            });

            cropper.bind({
                url: e.target.result,
                orientation: 0
            });

            document.getElementById("rotate").onclick = function () {
                cropper.rotate(90);
            }

            document.getElementById("submit").onclick = async function () {
                //hide controls
                document.getElementById("crop-controls").hidden = true;

                // show spinner
                document.getElementById("upload-spinner").hidden = false;

                var formData = new FormData();
                var f = new File([await cropper.result("blob")], "image.png", { type: "image/png" })

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