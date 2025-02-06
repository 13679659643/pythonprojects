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


function getUUID(n, href, cookie) {
    /**
     * n  "/sz/api/point/check.ajax"
     * o undefined
     * @type {{bw: number, bh: number}}
     */
    var r = {
            "bw": 1699,
            "bh": 941
        }
        , a = href
        ,
        d = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        , c = cookie
        , s = 1e9 * Math.random() << 0
        , p = (new Date).getTime()
        , m = t(e([r.bw + "" + r.bh, a, d, c, s, p, n].join("-"))).slice(20);
    return m + "-" + p.toString(16)
}

function o() {
    for (var n = document.cookie.split(/;\s?/), o = {}, e = 0; e < n.length; e++) {
        var t = n[e].split("=");
        try {
            o[t[0]] = decodeURIComponent(t[1])
        } catch (n) {
        }
    }
    return o
}

function e(n) {
    function o(n, o) {
        return n << o | n >>> 32 - o
    }

    var e = [1518500249, 1859775393, 2400959708, 3395469782]
        , t = [1732584193, 4023233417, 2562383102, 271733878, 3285377520];
    if ("string" == typeof n) {
        var i = unescape(encodeURIComponent(n));
        n = new Array(i.length);
        for (c = 0; c < i.length; c++)
            n[c] = i.charCodeAt(c)
    }
    n.push(128);
    for (var r = n.length / 4 + 2, a = Math.ceil(r / 16), d = new Array(a), c = 0; c < a; c++) {
        d[c] = new Array(16);
        for (var s = 0; s < 16; s++)
            d[c][s] = n[64 * c + 4 * s] << 24 | n[64 * c + 4 * s + 1] << 16 | n[64 * c + 4 * s + 2] << 8 | n[64 * c + 4 * s + 3]
    }
    d[a - 1][14] = 8 * (n.length - 1) / Math.pow(2, 32),
        d[a - 1][14] = Math.floor(d[a - 1][14]),
        d[a - 1][15] = 8 * (n.length - 1) & 4294967295;
    for (c = 0; c < a; c++) {
        for (var p = new Array(80), m = 0; m < 16; m++)
            p[m] = d[c][m];
        for (m = 16; m < 80; m++)
            p[m] = o(p[m - 3] ^ p[m - 8] ^ p[m - 14] ^ p[m - 16], 1);
        for (var w = t[0], f = t[1], g = t[2], u = t[3], _ = t[4], m = 0; m < 80; m++) {
            var h = Math.floor(m / 20)
                , l = o(w, 5) + function (n, o, e, t) {
                switch (n) {
                    case 0:
                        return o & e ^ ~o & t;
                    case 1:
                        return o ^ e ^ t;
                    case 2:
                        return o & e ^ o & t ^ e & t;
                    case 3:
                        return o ^ e ^ t
                }
            }(h, f, g, u) + _ + e[h] + p[m] >>> 0;
            _ = u,
                u = g,
                g = o(f, 30) >>> 0,
                f = w,
                w = l
        }
        t[0] = t[0] + w >>> 0,
            t[1] = t[1] + f >>> 0,
            t[2] = t[2] + g >>> 0,
            t[3] = t[3] + u >>> 0,
            t[4] = t[4] + _ >>> 0
    }
    return [t[0] >> 24 & 255, t[0] >> 16 & 255, t[0] >> 8 & 255, 255 & t[0], t[1] >> 24 & 255, t[1] >> 16 & 255, t[1] >> 8 & 255, 255 & t[1], t[2] >> 24 & 255, t[2] >> 16 & 255, t[2] >> 8 & 255, 255 & t[2], t[3] >> 24 & 255, t[3] >> 16 & 255, t[3] >> 8 & 255, 255 & t[3], t[4] >> 24 & 255, t[4] >> 16 & 255, t[4] >> 8 & 255, 255 & t[4]]
}

function t(n) {
    for (var o = "", e = 0; e < n.length; e++) {
        var t = n[e].toString(16);
        o += t = 1 === t.length ? "0" + t : t
    }
    return o
}

function get_ajax_au_header(ajax_url, html_url, cookie) {
    var i = (new Date).getTime();
    uuid = getUUID(ajax_url, html_url, cookie)
    User_mup = i;
    User_mnp = createHash(ajax_url + uuid + i + "372ad2c2b6");   //md5createFun.createHash
    //x_pin=getPinCookie("pin")
    return [uuid,User_mup,User_mnp]
}

//var i = (new Date).getTime();
// ajax_url = "/sz/api/point/check.ajax";
// uuid = getUUID(ajax_url, "https://sz.jd.com/sz/view/dealAnalysis/dealSummarys.html", "__jdv=56585130|direct|-|none|-|1730684905590; __jdu=1730684905590780843961; TrackID=1T9dnQHv22DLK-lxxGklBppqk1NsNXykzcGbo_hG5BrnadOKcuyoUkde2I3Mxn30zUpOCvURClB9sJwUytHRq-6STlsrfXLDdqmjEDlEozSKvhX8Il4CyqXLsm5HtkncM; pinId=X7TpUFLZhqAIkxrNKzWhVA; pin=MODYF%E6%97%97%E8%88%B0%E5%BA%97; unick=5v1p2d06w43jzs; ceshi3.com=000; _tp=cz%2B%2BvZywjFpdup%2BrVO4dfmXTzJMFca7SoSD1Wfd9esPdDf6wa%2BxcJb3PxfGsE%2B2x; __USE_NEW_PAGEFRAME__=true; __USE_NEW_PAGEFRAME_VERSION__=v11; 3AB9D23F7A4B3CSS=jdd03WRYR6KHVB6FJMSXKRLN6NSRA4VIWH346LBRYAMJM27OSN5RH7BXH2LOT5GC5GRQKQBUABN5XIJCIPK4TKQMGBY7A44AAAAMS6UN5X6IAAAAADZCSES7O57J3RUX; _base_=YKH2KDFHMOZBLCUV7NSRBWQUJPBI7JIMU5R3EFJ5UDHJ5LCU7R2NILKK5UJ6GLA2RGYT464UKXAI4Z6HPCTN4UQM3WHVQ4ENFP57OC3MIMUATWESPI2RXL5GIXQZJLKCCQAVH6KGSNCO5PICBUSRLIQBSRZELA6E4S4L2GLWBLTAIW5N6ZGEONMNNA5DQRDPVL52KNRE2QP7OXMDMXGJAUP3WAG4MEKLVTSGRNFRP2B32A35AG2X7VYZOV5WJU5S6UIIGXPFV7GFKACVUU62VC24YPY7YWSXACMC4ZXUDHE3E5PQNFZ34PXHCQ6VIW32TGZQEHB2XGMD6MM56KNRS73AIWNJX6LYXNCG4G5RWQLTU5YNVGJ72ITKUVT57MKB; language=zh_CN; 3AB9D23F7A4B3C9B=WRYR6KHVB6FJMSXKRLN6NSRA4VIWH346LBRYAMJM27OSN5RH7BXH2LOT5GC5GRQKQBUABN5XIJCIPK4TKQMGBY7A44; __jda=251704139.1730684905590780843961.1730684906.1730684906.1730689081.2; __jdc=251704139; is_sz_old_version=false; __jdb=251704139.10.1730684905590780843961|2.1730689081")
// User_mup = i;
// User_mnp = createHash(ajax_url + uuid + i + "372ad2c2b6");   //md5createFun.createHash
// x_pin=getPinCookie("pin");
// console.log(uuid)
// console.log(User_mnp);
