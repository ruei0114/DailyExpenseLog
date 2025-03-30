function over(btn){
    btn.style.backgroundColor ="#262626";
}

function out(btn){
    btn.style.backgroundColor ="#191919";
}

function overFilterBtn(btn){
    btn.style.backgroundColor ="#262626";
}

function outFilterBtn(btn){
    btn.style.backgroundColor = "#191919";
}

let light_gray="#373737";
let gray="#5a5a5a";
let brown="#603b2c";
let orange="#854c1d";
let yellow="#89632a";
let green="#2b593f";
let blue="#28456c";
let purple="#492f64"
let pink="#69314c"
let red="#6e3630"
var catColors = [brown, orange, yellow, green, blue, purple, pink, red];
var in_outColors=[light_gray, gray];

let categories=[];

function updateCategoryOptions() {
    var inOutInput = document.getElementById('io');
    var categoryInput = document.getElementById('catg');
    var typesDatalist = document.getElementById('types');
    categoryInput.style.display='';
    typesDatalist.innerHTML = ''; // Clear existing options

    let in_outInput = inOutInput.value;
    // 获取category在数组中的索引
    var income_cost = ['收入', '支出']
    let in_outIndex = income_cost.indexOf(in_outInput);

    // 如果category存在且索引有效，则应用背景颜色
    if (in_outIndex !== -1) {
        // 计算背景颜色索引（categoryIndex mod 10）
        var colorIndex = in_outIndex % 10;

        // 获取对应颜色
        var selectedColor = in_outColors[colorIndex];

        // 应用背景颜色
        inOutInput.style.backgroundColor = selectedColor;
        inOutInput.style.borderRadius = '4px';
    }

    categories = [];
    if (inOutInput.value === '收入') {
        categories = ['工資', '獎金', '投資', '副業'];
    } else if (inOutInput.value === '支出') {
        categories = ['飲食', '日常用品', '交通', '水電瓦斯', '電話網路', '服飾', '娛樂', '醫療保健', '美容美髮', '學習深造', '交際應酬', '保險', '稅金'];
    }

    categories.forEach(function (category) {
        var option = document.createElement('option');
        option.value = category;
        typesDatalist.appendChild(option);
    });
}

function updateTypeOptions(){
    var catgInput = document.getElementById('catg');
    let catgVal = catgInput.value;
    let catgIndex = categories.indexOf(catgVal);

    // 如果category存在且索引有效，则应用背景颜色
    if (catgIndex !== -1) {
        // 计算背景颜色索引（categoryIndex mod 10）
        var colorIndex = catgIndex % 7;

        // 获取对应颜色
        var selectedColor = catColors[colorIndex];

        // 应用背景颜色
        catgInput.style.backgroundColor = selectedColor;
        catgInput.style.borderRadius = '4px';
    }
}

function submitForm() {
    var form = document.getElementById('expenseForm');
    var formData = new FormData(form);
    document.getElementById('itm').value='';
    document.getElementById('dt').value='';
    document.getElementById('io').value='';
    document.getElementById('io').style.backgroundColor='#191919';
    document.getElementById('catg').value='';
    document.getElementById('catg').style.display="none";
    document.getElementById('catg').style.backgroundColor="#191919";
    document.getElementById('amt').value='';
    document.getElementById('types').innerHTML='';
    document.getElementById('message-container').innerHTML='';

    // Send the data to the Flask backend using AJAX
    fetch('/save_data', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // 處理 JSON 回應
        if (data.status === 'success') {
            // 成功的情況
            showMessage('success', 'Data saved successfully!');
        } else {
            // 錯誤的情況
            showMessage('error', data.message);
        }
        //console.log('Data sent successfully:', data);
    })
    .catch(error => {
        console.error('Error sending data:', error);
        showMessage('error', 'An error occurred while sending data.');
    });
}

function showMessage(type, message) {
     // 在 message-container 元素中顯示訊息和 SVG 圖標
     var messageContainer = document.getElementById('message-container');
     var iconHTML = '<svg role="graphics-symbol" viewBox="0 0 14 22" class="boltFilled" style="width: 14px; height: 14px; fill: rgb(217, 158, 53); flex-shrink: 0; margin-right: 10px;"><path d="M0 12.117c0 .38.293.664.703.664h5.518l-2.91 7.91c-.381 1.006.664 1.543 1.318.723l8.877-11.094c.166-.205.254-.4.254-.625 0-.371-.293-.664-.703-.664H7.539l2.91-7.91C10.83.115 9.785-.422 9.131.408L.254 11.492c-.166.215-.254.41-.254.625z"></path></svg>';
     var messageHTML = `<div class="message">${message}</div>`;
     
     // 使用 flexbox 佈局，將內容置中
     messageContainer.innerHTML = `<div style="display: flex; align-items: center; justify-content: flex-end;">${iconHTML}${messageHTML}</div>`;
 }

function clickFilter(){
    let filterStatus = document.getElementById('filterForm')
    if (filterStatus.style.display==='none'){
        document.getElementById('filterBtn').style.color = '#2383e2';
        filterStatus.style.display = '';
    }else{
        document.getElementById('filterBtn').style.color = '#626262';
        filterStatus.style.display = 'none';
    } 
}

function applyFilter() {
    // 獲取日期選擇器的值
    var selectedDate = document.getElementById('dateFilter').value;
  
    // 使用fetch向Flask後端發送請求
    fetch('/apply_filter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ dateFilter: selectedDate }),
    })
    .then(response => response.json())
    .then(data => {
      // 在控制台中打印從後端獲取的數據
      console.log('Filtered Data:', data);
      // 在這裡進行進一步的處理，例如更新UI顯示
      displayFilteredData(data);
    })
    .catch(error => {
      console.error('Error applying filter:', error);
    });
}


function displayFilteredData(data) {
    document.getElementById('costIncomeFrame').style.display = 'flex';
    var filteredDataElement = document.getElementById('filteredData');
    document.getElementById('filteredHead').style.display='';

    // 清空之前的內容
    filteredDataElement.innerHTML = '';
    let totalCost = 0;
    let totalIncome = 0;
    let difference = 0;

    // 顯示新的數據
    data.forEach(entry => {
        // Create a parent div for each entry
    var entryElement = document.createElement('div');
    entryElement.className = 'row';

    // Create and append content divs
    var contentDiv1 = document.createElement('div');
    contentDiv1.className = 'content col';
    contentDiv1.innerHTML=entry[1];
    entryElement.appendChild(contentDiv1);

    var contentDiv2 = document.createElement('div');
    contentDiv2.className = 'content col';
    contentDiv2.innerHTML = entry[2].replace(/-/g, '/');
    entryElement.appendChild(contentDiv2);

    var contentDiv3 = document.createElement('div');
    contentDiv3.className = 'content col';
    var contentDiv3_1 = document.createElement('div');
    var filtcatg= [];
    if (entry[3]==='收入'){
        contentDiv3_1.style = 'border-radius: 4px;  padding: 2px 5px 2px 5px; background-color: #373737'
        filtcatg = ['工資', '獎金', '投資', '副業'];
        totalIncome += parseFloat(entry[5])
    }else{
        contentDiv3_1.style = 'border-radius: 4px;  padding: 2px 5px 2px 5px; background-color: #5a5a5a'
        filtcatg = ['飲食', '日常用品', '交通', '水電瓦斯', '電話網路', '服飾', '娛樂', '醫療保健', '美容美髮', '學習深造', '交際應酬', '保險', '稅金'];
        totalCost += parseFloat(entry[5]);
    }
    difference = totalCost - totalIncome;
    contentDiv3_1.textContent = entry[3];
    contentDiv3.appendChild(contentDiv3_1);

    var contentDiv3_2 = document.createElement('div');
    let catgIndex = filtcatg.indexOf(entry[4]);
    var colorIndex = catgIndex % 7;
    var selectedColor = catColors[colorIndex];
    contentDiv3_2.style = 'border-radius: 4px;  padding: 2px 5px 2px 5px; margin-left: 7px';
    contentDiv3_2.style.backgroundColor = selectedColor;
    console.log(colorIndex, selectedColor);
    contentDiv3_2.textContent = entry[4];
    contentDiv3.appendChild(contentDiv3_2);
    entryElement.appendChild(contentDiv3);

    var contentDiv4 = document.createElement('div');
    contentDiv4.className = 'content col';
    contentDiv4.innerHTML = entry[5];
    entryElement.appendChild(contentDiv4);

    // Append the entry element to the filteredDataElement
    filteredDataElement.appendChild(entryElement);
    showFilteredCostIncome(totalCost, totalIncome, difference);
    });
}

function showFilteredCostIncome(totalCost, totalIncome, difference) {
    document.getElementById('costIncomeFrame').style.display = 'flex';
    document.getElementById('totalCost').textContent = String(totalCost);
    document.getElementById('totalIncome').textContent = String(totalIncome);
    diff = document.getElementById('difference');
    if (difference > 0){
        diff.textContent = "shortfall: " + String(difference);
    }else{
        diff.textContent = "surplus: " + String(-difference);
    }
}

function clearFilter(){
    document.getElementById('dateFilter').value = '';
    document.getElementById('filterForm').style.display = 'none';
    document.getElementById('filterBtn').style.color = '#626262';
    document.getElementById('filteredHead').style.display = 'none';
    document.getElementById('filteredData').innerHTML = '';
    document.getElementById('costIncomeFrame').style.display = 'none';
}