document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('anime-url');
    const downloadBtn = document.getElementById('download-btn');
    const filterBtn = document.getElementById('filter-btn');
    const filterMenu = document.getElementById('filter-menu');
    const downloadMenu = document.getElementById('download-menu');
    
    input.addEventListener('input', function() {
        const inputValue = input.value;
        const pattern = /^(https:\/\/)?(www\.)?anime-sama\.fr\/catalogue\/[^\/]+\/[^\/]+\/(vostfr|vf)\/?$/;
        
        if (pattern.test(inputValue)) {
            downloadBtn.classList.add('enabled');
            input.style.color = 'white';
        } else {
            downloadBtn.classList.remove('enabled');
            input.style.color = 'rgb(204, 11, 11)';
        }
    });

    filterBtn.addEventListener('click', function(event) {
        if (!filterBtn.classList.contains('disabled')) {
            event.stopPropagation();
            filterMenu.style.display = filterMenu.style.display === 'none' || filterMenu.style.display === '' ? 'block' : 'none';
        }
    });

    document.addEventListener('click', function(event) {
        if (!filterMenu.contains(event.target) && event.target !== filterBtn) {
            filterMenu.style.display = 'none';
        }
        if (!downloadMenu.contains(event.target) && event.target !== downloadBtn) {
            downloadMenu.style.display = 'none';
            filterBtn.classList.remove('disabled');
        }

    });

        filterMenu.addEventListener('click', function(event) {
            event.stopPropagation();
        });
        downloadMenu.addEventListener('click', function(event) {
            event.stopPropagation();
        });


    document.querySelectorAll('.checkbox-group').forEach(group => {
    group.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                group.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    if (cb !== this) {
                        cb.checked = false;
                    }
                });
            }
        });
    });
});

 downloadBtn.addEventListener('click', function(event) {
  

    if (downloadBtn.classList.contains('enabled')) {
        event.stopPropagation();
        filterMenu.style.display = 'none';
    if (downloadMenu.style.display === 'none' || downloadMenu.style.display === '') {
        downloadMenu.style.display = 'block';
        filterBtn.classList.add('disabled');
    } else {
        downloadMenu.style.display = 'none';
        filterBtn.classList.remove('disabled');
    
    }
        // Get range slider values
        const rangeSlider = $(".js-range-slider").data("ionRangeSlider");
        const rangeValues = rangeSlider.result;

        // Get selected quality
        const selectedQuality = document.querySelector('input[id="quality"]:checked').value;

        // Get selected version
        const selectedVersion = document.querySelector('input[id="version"]:checked').value;

        const data = {
        rangeFrom: rangeValues.from,
        rangeTo: rangeValues.to,
        quality: selectedQuality,
        version: selectedVersion,
        url : input.value
    }
    downloadMenu.innerHTML = '<p>Please wait ...</p>';

    // Send the data to Flask backend using fetch
    fetch('/process_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        downloadMenu.innerHTML = ''; // Clear any existing content
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy All Links';
        copyButton.style.display = 'block';
        copyButton.style.marginBottom = '10px';
        copyButton.addEventListener('click', function() {
            const links = data.output.join('\n');
            navigator.clipboard.writeText(links).then(() => {
                alert('Links copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });});
        downloadMenu.appendChild(copyButton);
        
        data.output.forEach(item => {
            const pElement = document.createElement('p');
            const linkElement = document.createElement('a');
            linkElement.href = item;
            linkElement.textContent = item;
            linkElement.title = item; // Show the full link on hover
            pElement.appendChild(linkElement);
            downloadMenu.appendChild(pElement);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
        downloadMenu.innerHTML = '<p>There was an error processing your request.</p>';

    });
} else {
    filterBtn.classList.remove('disabled');}
});

$(document).ready(function() {
        $(".js-range-slider").ionRangeSlider({
            skin: "round",
            type: "double",
            min: 1,
            max: 50,
            step: 1,
            from: 1,
            to: 50,
            prettify: function (num) {
                if (num === 1) return "Start";
                if (num === 50) return "End";
                return num;
            },
            onStart: function (data) {
                handleLabels(data);
            },
            onChange: function (data) {
                handleLabels(data);
            }
        });

        function handleLabels(data) {
            var from = data.from;
            var to = data.to;

            if (from === 1) {
                $(".irs-from").text("Start");
            }
            if (to === 50) {
                $(".irs-to").text("End");
            }
            if (from !== 1) {
                $(".irs-from").text(from);
            }
            if (to !== 50) {
                $(".irs-to").text(to);
            }
        }
    });
});