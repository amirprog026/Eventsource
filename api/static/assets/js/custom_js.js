
temp=0;
function updateTrackIDStatus() {
    fetch('/track-status')
        .then(response => response.json())
        .then(data => {
            const queuedCount = document.getElementById('queued-count');
            const storedCount = document.getElementById('stored-count');
            const storedchart= document.getElementById('storedchart');
            //const trackidList = document.getElementById('trackid-list');
            //trackidList.innerHTML = '';  // Clear the list
            if (temp==0){temp=data;}
            let dif_stored=data.stored_count-temp.stored_count;
            let dif_queued=data.queued_count-temp.queued_count;
            temp=data;
            queuedCount.innerHTML = ` <h4 class="mb-3" >${data.queued_count}</h4>
                     <div class="d-flex align-items-center gap-2">
                      <div class="widget-icon-small bg-light-danger text-danger">
                       
                      </div>
                      <p class="mb-0">${dif_queued} last 5sec</p>
                   </div>    `;
            storedCount.innerHTML = `<h3 class="mb-2" >${data.stored_count}</h3>
                    <div class="d-flex align-items-center gap-2">
                       <div class="widget-icon-small bg-light-danger text-danger">
                        
                       </div>
                       <p class="mb-0">${dif_stored} last 5sec</p>
                    </div>`;
              
             // storedChart.setAttribute('data-percent', (data.stored_count /data.queued_count)*100);
             // storedChart.dataset.percent =(data.stored_count /data.queued_count)*100;
   
        })
        .catch(error => console.error('Error fetching track status:', error));
}

function calculateTrend(values) {
      if (values.length < 2) {
        return 0; // No comparison possible if less than 2 items
    }

    // Get the last value in the array
    let lastValue = values[values.length - 1];

    // Calculate the average of all previous values
    let prevValues = values.slice(0, -1);
    let avgPrev = prevValues.reduce((sum, val) => sum + val, 0) / prevValues.length;

    // Calculate the percent change between the last value and the average
    let percentChange = ((lastValue - avgPrev) / avgPrev) * 100;

    return percentChange.toFixed(2);  // Returning percent change as a rounded string
}
window.onload = (event) => {
    
    setInterval(updateTrackIDStatus, 5000);
    updateTrackIDStatus();  // Initial call to populate the list
    let salechange=document.getElementById('trendpercent');
     salechange.innerHTML=calculateTrend(values1);
  };

