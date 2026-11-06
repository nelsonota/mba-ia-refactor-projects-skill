'use strict';

function validateCheckout(req, res, next) {
    const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body || {};
    if (!userName || !email || !password || !courseId || !cardNumber) {
        return res.status(400).send('Bad Request');
    }
    req.validatedCheckout = { userName, email, password, courseId, cardNumber };
    return next();
}

module.exports = { validateCheckout };
