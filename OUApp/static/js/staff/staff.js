function reservationToRent(reservation_id) {
    if (confirm("Bạn chắc chắn lập phiếu thuê không?") == true) {
        fetch(`/api/reservations/${reservation_id}`, {
            method: "put",
            body: JSON.stringify({
                "reservation_id": reservation_id
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then((data) => {
            alert("Thành công")
            window.location = "/staff/rent/reservations"
        })
    }
}


function pay(reservation_id) {
    if (confirm("Bạn có chắc chắn đã nhận tiền và xác nhận thanh toán không?") == true) {
        fetch(`/api/reservations/pay/${reservation_id}`, {
            method: "put",
            body: JSON.stringify({
                "reservation_id": reservation_id
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then((data) => {
            alert("Thành công")
            window.location = 'staff/booking'
        })
    }
}


function logoff() {
    if (confirm("Bạn có chắc chắn muốn đăng xuất không?") == true) {
        fetch(`/api/staff/logoff`).then(res => res.json()).then((data) => {
            window.location = "/login"
        })
    }
}


function goBook() {
    if (confirm("Vui lòng tiến hành đặt phòng cho khách sau đó thực hiện lập phiếu thuê") == true) {
        window.location = "/booking"
    }
}