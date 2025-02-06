function get_ajax_au_header(e) {
    h = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (function (e) {
            var t = 16 * Math.random() | 0;
            return ("x" === e ? t : 3 & t | 8).toString(16)
        }
    ));
    y = e.split("?")[0];
    v = y.replace(/^http(s)?:\/\/(.*?)\//, "/").replace(/\s+/g, "").replace(/\?.*/, "");
    w = (new Date).getTime();
    b = createHash(v + h + w + "372ad2c2b6");
    // h uuid
    // w User-mup
    // b User-mnp
    return [h, w, b]

}

function createHash(e) {
    if (null === e)
        return null;
    var t, n, a, i, r, o, l, c, s, d, u = function (e, t) {
            return e << t | e >>> 32 - t
        }, p = function (e, t) {
            var n, a, i, r, o;
            return i = 2147483648 & e,
                r = 2147483648 & t,
                n = 1073741824 & e,
                a = 1073741824 & t,
                o = (1073741823 & e) + (1073741823 & t),
                n & a ? 2147483648 ^ o ^ i ^ r : n | a ? 1073741824 & o ? 3221225472 ^ o ^ i ^ r : 1073741824 ^ o ^ i ^ r : o ^ i ^ r
        }, g = function (e, t, n) {
            return e & t | ~e & n
        }, m = function (e, t, n) {
            return e & n | t & ~n
        }, f = function (e, t, n) {
            return e ^ t ^ n
        }, h = function (e, t, n) {
            return t ^ (e | ~n)
        }, b = function (e, t, n, a, i, r, o) {
            return e = p(e, p(p(g(t, n, a), i), o)),
                p(u(e, r), t)
        }, v = function (e, t, n, a, i, r, o) {
            return e = p(e, p(p(m(t, n, a), i), o)),
                p(u(e, r), t)
        }, y = function (e, t, n, a, i, r, o) {
            return e = p(e, p(p(f(t, n, a), i), o)),
                p(u(e, r), t)
        }, w = function (e, t, n, a, i, r, o) {
            return e = p(e, p(p(h(t, n, a), i), o)),
                p(u(e, r), t)
        }, D = function (e) {
            for (var t, n = e.length, a = n + 8, i = (a - a % 64) / 64, r = 16 * (i + 1), o = new Array(r - 1), l = 0, c = 0; c < n;)
                t = (c - c % 4) / 4,
                    l = c % 4 * 8,
                    o[t] = o[t] | e.charCodeAt(c) << l,
                    c++;
            return t = (c - c % 4) / 4,
                l = c % 4 * 8,
                o[t] = o[t] | 128 << l,
                o[r - 2] = n << 3,
                o[r - 1] = n >>> 29,
                o
        }, k = function (e) {
            var t, n, a = "", i = "";
            for (n = 0; n <= 3; n++)
                t = e >>> 8 * n & 255,
                    i = "0" + t.toString(16),
                    a += i.substr(i.length - 2, 2);
            return a
        }, x = [], $ = 7, C = 12, S = 17, I = 22, M = 5, T = 9, O = 14, A = 20, E = 4, P = 11, R = 16, F = 23, V = 6,
        B = 10, W = 15, H = 21;
    for (x = D(e),
             l = 1732584193,
             c = 4023233417,
             s = 2562383102,
             d = 271733878,
             t = x.length,
             n = 0; n < t; n += 16)
        a = l,
            i = c,
            r = s,
            o = d,
            l = b(l, c, s, d, x[n + 0], $, 3614090360),
            d = b(d, l, c, s, x[n + 1], C, 3905402710),
            s = b(s, d, l, c, x[n + 2], S, 606105819),
            c = b(c, s, d, l, x[n + 3], I, 3250441966),
            l = b(l, c, s, d, x[n + 4], $, 4118548399),
            d = b(d, l, c, s, x[n + 5], C, 1200080426),
            s = b(s, d, l, c, x[n + 6], S, 2821735955),
            c = b(c, s, d, l, x[n + 7], I, 4249261313),
            l = b(l, c, s, d, x[n + 8], $, 1770035416),
            d = b(d, l, c, s, x[n + 9], C, 2336552879),
            s = b(s, d, l, c, x[n + 10], S, 4294925233),
            c = b(c, s, d, l, x[n + 11], I, 2304563134),
            l = b(l, c, s, d, x[n + 12], $, 1804603682),
            d = b(d, l, c, s, x[n + 13], C, 4254626195),
            s = b(s, d, l, c, x[n + 14], S, 2792965006),
            c = b(c, s, d, l, x[n + 15], I, 1236535329),
            l = v(l, c, s, d, x[n + 1], M, 4129170786),
            d = v(d, l, c, s, x[n + 6], T, 3225465664),
            s = v(s, d, l, c, x[n + 11], O, 643717713),
            c = v(c, s, d, l, x[n + 0], A, 3921069994),
            l = v(l, c, s, d, x[n + 5], M, 3593408605),
            d = v(d, l, c, s, x[n + 10], T, 38016083),
            s = v(s, d, l, c, x[n + 15], O, 3634488961),
            c = v(c, s, d, l, x[n + 4], A, 3889429448),
            l = v(l, c, s, d, x[n + 9], M, 568446438),
            d = v(d, l, c, s, x[n + 14], T, 3275163606),
            s = v(s, d, l, c, x[n + 3], O, 4107603335),
            c = v(c, s, d, l, x[n + 8], A, 1163531501),
            l = v(l, c, s, d, x[n + 13], M, 2850285829),
            d = v(d, l, c, s, x[n + 2], T, 4243563512),
            s = v(s, d, l, c, x[n + 7], O, 1735328473),
            c = v(c, s, d, l, x[n + 12], A, 2368359562),
            l = y(l, c, s, d, x[n + 5], E, 4294588738),
            d = y(d, l, c, s, x[n + 8], P, 2272392833),
            s = y(s, d, l, c, x[n + 11], R, 1839030562),
            c = y(c, s, d, l, x[n + 14], F, 4259657740),
            l = y(l, c, s, d, x[n + 1], E, 2763975236),
            d = y(d, l, c, s, x[n + 4], P, 1272893353),
            s = y(s, d, l, c, x[n + 7], R, 4139469664),
            c = y(c, s, d, l, x[n + 10], F, 3200236656),
            l = y(l, c, s, d, x[n + 13], E, 681279174),
            d = y(d, l, c, s, x[n + 0], P, 3936430074),
            s = y(s, d, l, c, x[n + 3], R, 3572445317),
            c = y(c, s, d, l, x[n + 6], F, 76029189),
            l = y(l, c, s, d, x[n + 9], E, 3654602809),
            d = y(d, l, c, s, x[n + 12], P, 3873151461),
            s = y(s, d, l, c, x[n + 15], R, 530742520),
            c = y(c, s, d, l, x[n + 2], F, 3299628645),
            l = w(l, c, s, d, x[n + 0], V, 4096336452),
            d = w(d, l, c, s, x[n + 7], B, 1126891415),
            s = w(s, d, l, c, x[n + 14], W, 2878612391),
            c = w(c, s, d, l, x[n + 5], H, 4237533241),
            l = w(l, c, s, d, x[n + 12], V, 1700485571),
            d = w(d, l, c, s, x[n + 3], B, 2399980690),
            s = w(s, d, l, c, x[n + 10], W, 4293915773),
            c = w(c, s, d, l, x[n + 1], H, 2240044497),
            l = w(l, c, s, d, x[n + 8], V, 1873313359),
            d = w(d, l, c, s, x[n + 15], B, 4264355552),
            s = w(s, d, l, c, x[n + 6], W, 2734768916),
            c = w(c, s, d, l, x[n + 13], H, 1309151649),
            l = w(l, c, s, d, x[n + 4], V, 4149444226),
            d = w(d, l, c, s, x[n + 11], B, 3174756917),
            s = w(s, d, l, c, x[n + 2], W, 718787259),
            c = w(c, s, d, l, x[n + 9], H, 3951481745),
            l = p(l, a),
            c = p(c, i),
            s = p(s, r),
            d = p(d, o);
    var N = k(l) + k(c) + k(s) + k(d);
    return N.toLowerCase()
}

//url = "https://ppzh.jd.com/brand/dealAnalysis/dealDetail/getDealDetailData.ajax?thirdCategoryId=all&brandId=all&channel=0&shopType=all&date=2024-11-17&endDate=2024-11-17&startDate=2024-11-17&pageSize=10&pageNum=1"
//url = "https://ppzh.jd.com/brand/dealAnalysis/dealDetail/getDealDetailData.ajax"
//console.log(get_ajax_au_header(url))