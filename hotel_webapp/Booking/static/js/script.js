
let room_type = null;
document.addEventListener('DOMContentLoaded', function () {
    let urlParams = window.location.search;
    queryString = urlParams.substring(1);
    queryString = decodeURIComponent(queryString);
    // console.log(queryString);
    let parsedData = JSON.parse(queryString);
    if (parsedData === "") {
        parsedData = null;
    }
    // console.log(`fffffffffff`, { parsedData });
    const checkIn = parsedData.check_in;
    const checkOut = parsedData.check_out;
    // const noOfRooms = parsedData.no_of_room;
    const noOfAdults = parsedData.no_of_adult;
    const noOfChildren = parsedData.no_of_child;
    room_type = parsedData.room_type;
    // console.log(checkIn, checkOut, noOfAdults, noOfChildren)

    if (checkIn) {
        document.getElementById('form-checkIn-type').value = checkIn;
        document.getElementById('form-checkIn-type').readonly = true;  // Make the field readonly
    }

    if (checkOut) {
        document.getElementById('form-checkOut-type').value = checkOut;
        document.getElementById('form-checkOut-type').readonly = true;  // Make the field readonly
    }

    // if (room_type) {
    //     document.getElementById('form-room-type').value = room_type;
    // }

})

function add_booking(event) {
    event.preventDefault();

    fname = document.querySelector("#fname").value;
    lname = document.querySelector("#lname").value;
    phone_no = document.querySelector("#phone-no").value;
    email = document.querySelector("#email").value;
    // room_type = room_type;
    checkIn = document.querySelector("#form-checkIn-type").value;
    checkOut = document.querySelector("#form-checkOut-type").value;
    meal_field = document.querySelector("#form-meal");
    meal_type = meal_field.selectedIndex;
    meal_type = meal_field.value;
    adults = document.querySelectorAll(".adults");
    child = document.querySelectorAll(".child");
    rooms = document.querySelectorAll(".rooms");
    amount = document.getElementById("grand_total").value;
    // console.log("amount",amount)

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // console.log(emailRegex.test(email))
    
    if (fname === "" || fname.includes(" ") || lname.includes(" ") || phone_no.includes(" ") || email.includes(" ")|| lname === "" || phone_no === "" || email === "" || checkIn === "" || checkOut === "") {
        Swal.fire({
            title: "Please fill out all required fields",
            text: "You won't be able to proceed without completing them.",
            icon: "warning",
        })
    }
    else if(checkIn>=checkOut){
        // console.log(`checkIn:${checkIn},checkOut:${checkOut},${checkIn<checkOut}`)
        Swal.fire({
            title: "Enter Valid CHECK IN and CHECK OUT DATE's",
            text: "You won't be able to proceed without completing them.",
            icon: "warning",
        })
    }   
    else if (!emailRegex.test(email)){
        Swal.fire({
            title: "Invalid Email",
            text: "Please fill Email in Correct Format(e.g:hello@example.com)",
            icon: "warning",
        })
        return
    }
    else {
        let allRooms = 0;
        allRooms = rooms.length;
        // console.log(`allRooms ${allRooms}`);

        let allAdults = 0;
        for (let i = 0; i < adults.length; i++) {
            // console.log(adults[i].value);
            allAdults = allAdults + parseInt(adults[i].value);
            // console.log(allAdults);
        }
        // console.log("Sum_allAdults", allAdults);

        let allChild = 0;
        for (let i = 0; i < child.length; i++) {
            ;
            // console.log(child[i]);
            allChild = allChild + parseInt(child[i].value);
        }

        booking_data = {
            "fname": fname,
            "lname": lname,
            "phone_no": phone_no,
            "email": email,
            "room_type": room_type,
            "checkIn": checkIn,
            "checkOut": checkOut,
            "totalrooms": allRooms,
            "allAdults": allAdults,
            "allChild": allChild,
            "meal_type": meal_type,
            'amount' : amount,
        }

        console.log(booking_data);
        
        booking_data = JSON.stringify(booking_data);
        // console.log(booking_data)
        // var csrfToken = '{{csrf_token}}';  // This will inject the CSRF token into a JS variable

        base_url = window.location.hostname+'/payment/booking'
        fetch(base_url, {
            method: 'POST',
            headers: { "X-CSRFToken": '{{csrf_token}}' },
            body: booking_data,
        }).then(response =>
            response.json()
        ).then(data => {
            // console.log(data);
            if (data.reload){
                // console.log()
                window.location.reload()
            }
            else{
            // console.log(data['url']);
            window.location.href=data['url'];
            }
        })
    }
}

