window = {};
!function (e) {
    var t = {};

    function n(r) {
        if (t[r])
            return t[r].exports;
        var o = t[r] = {
            i: r,
            l: !1,
            exports: {}
        };
        return e[r].call(o.exports, o, o.exports, n),
            o.l = !0,
            o.exports
    }

    return n.m = e,
        n.c = t,
        n.d = function (e, t, r) {
            n.o(e, t) || Object.defineProperty(e, t, {
                enumerable: !0,
                get: r
            })
        }
        ,
        n.r = function (e) {
            "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {
                value: "Module"
            }),
                Object.defineProperty(e, "__esModule", {
                    value: !0
                })
        }
        ,
        n.t = function (e, t) {
            if (1 & t && (e = n(e)),
            8 & t)
                return e;
            if (4 & t && "object" == typeof e && e && e.__esModule)
                return e;
            var r = Object.create(null);
            if (n.r(r),
                Object.defineProperty(r, "default", {
                    enumerable: !0,
                    value: e
                }),
            2 & t && "string" != typeof e)
                for (var o in e)
                    n.d(r, o, function (t) {
                        return e[t]
                    }
                        .bind(null, o));
            return r
        }
        ,
        n.n = function (e) {
            var t = e && e.__esModule ? function () {
                        return e.default
                    }
                    : function () {
                        return e
                    }
            ;
            return n.d(t, "a", t),
                t
        }
        ,
        n.o = function (e, t) {
            return Object.prototype.hasOwnProperty.call(e, t)
        }
        ,
        n.p = "",
        n(n.s = 0), window.ccc = n
}
([(e, t, n) => {
    "use strict";

    function r(e, t) {
        return e(t = {
            exports: {}
        }, t.exports),
            t.exports
    }

    function i(e, t) {
        var n, r, i, a = 0, s = !t && 0 !== t && "function" == typeof window.requestAnimationFrame;

        function o(e, t) {
            return s ? (window.cancelAnimationFrame(i),
                window.requestAnimationFrame(e)) : setTimeout(e, t)
        }

        function u() {
            var t = n
                , a = r;
            return i = n = r = void 0,
                e.apply(a, t)
        }

        t = +t || 0;
        var c = [1, 2, 3]
            , l = c[0]
            , h = c[1]
            , d = c[2];
        return console.log(l, h, d),
            function () {
                for (var e = [], s = 0; s < arguments.length; s++)
                    e[s] = arguments[s];
                var c = Date.now()
                    , l = c - a
                    , h = t - l;
                n = e,
                    r = this,
                void 0 === i && (i = o(u, 0 === a ? t : h < 0 ? 0 : Math.abs(h))),
                    a = c
            }
    }

    n.d(t, {
        Ds: () => i,
        Fs: () => h,
        sH: () => d,
        o9: () => f
    }),
        r((function (e, t) {
                var n;
                n = function () {
                    function e() {
                        for (var e = 0, t = {}; e < arguments.length; e++) {
                            var n = arguments[e];
                            for (var r in n)
                                t[r] = n[r]
                        }
                        return t
                    }

                    function t(e) {
                        return e.replace(/(%[0-9A-Z]{2})+/g, decodeURIComponent)
                    }

                    return function n(r) {
                        function i() {
                        }

                        function a(t, n, a) {
                            if ("undefined" != typeof document) {
                                "number" == typeof (a = e({
                                    path: "/"
                                }, i.defaults, a)).expires && (a.expires = new Date(1 * new Date + 864e5 * a.expires)),
                                    a.expires = a.expires ? a.expires.toUTCString() : "";
                                try {
                                    var s = JSON.stringify(n);
                                    /^[\{\[]/.test(s) && (n = s)
                                } catch (e) {
                                }
                                n = r.write ? r.write(n, t) : encodeURIComponent(String(n)).replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g, decodeURIComponent),
                                    t = encodeURIComponent(String(t)).replace(/%(23|24|26|2B|5E|60|7C)/g, decodeURIComponent).replace(/[\(\)]/g, escape);
                                var o = "";
                                for (var u in a)
                                    a[u] && (o += "; " + u,
                                    !0 !== a[u] && (o += "=" + a[u].split(";")[0]));
                                return document.cookie = t + "=" + n + o
                            }
                        }

                        function s(e, n) {
                            if ("undefined" != typeof document) {
                                for (var i = {}, a = document.cookie ? document.cookie.split("; ") : [], s = 0; s < a.length; s++) {
                                    var o = a[s].split("=")
                                        , u = o.slice(1).join("=");
                                    n || '"' !== u.charAt(0) || (u = u.slice(1, -1));
                                    try {
                                        var c = t(o[0]);
                                        if (u = (r.read || r)(u, c) || t(u),
                                            n)
                                            try {
                                                u = JSON.parse(u)
                                            } catch (e) {
                                            }
                                        if (i[c] = u,
                                        e === c)
                                            break
                                    } catch (e) {
                                    }
                                }
                                return e ? i[e] : i
                            }
                        }

                        return i.set = a,
                            i.get = function (e) {
                                return s(e, !1)
                            }
                            ,
                            i.getJSON = function (e) {
                                return s(e, !0)
                            }
                            ,
                            i.remove = function (t, n) {
                                a(t, "", e(n, {
                                    expires: -1
                                }))
                            }
                            ,
                            i.defaults = {},
                            i.withConverter = n,
                            i
                    }((function () {
                        }
                    ))
                }
                    ,
                    e.exports = n()
            }
        ));
    debugger;
    ;
    var a = r((function (e) {
            var t, n;
            t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
                n = {
                    rotl: function (e, t) {
                        return e << t | e >>> 32 - t
                    },
                    rotr: function (e, t) {
                        return e << 32 - t | e >>> t
                    },
                    endian: function (e) {
                        if (e.constructor == Number)
                            return 16711935 & n.rotl(e, 8) | 4278255360 & n.rotl(e, 24);
                        for (var t = 0; t < e.length; t++)
                            e[t] = n.endian(e[t]);
                        return e
                    },
                    randomBytes: function (e) {
                        for (var t = []; e > 0; e--)
                            t.push(Math.floor(256 * Math.random()));
                        return t
                    },
                    bytesToWords: function (e) {
                        for (var t = [], n = 0, r = 0; n < e.length; n++,
                            r += 8)
                            t[r >>> 5] |= e[n] << 24 - r % 32;
                        return t
                    },
                    wordsToBytes: function (e) {
                        for (var t = [], n = 0; n < 32 * e.length; n += 8)
                            t.push(e[n >>> 5] >>> 24 - n % 32 & 255);
                        return t
                    },
                    bytesToHex: function (e) {
                        for (var t = [], n = 0; n < e.length; n++)
                            t.push((e[n] >>> 4).toString(16)),
                                t.push((15 & e[n]).toString(16));
                        return t.join("")
                    },
                    hexToBytes: function (e) {
                        for (var t = [], n = 0; n < e.length; n += 2)
                            t.push(parseInt(e.substr(n, 2), 16));
                        return t
                    },
                    bytesToBase64: function (e) {
                        for (var n = [], r = 0; r < e.length; r += 3)
                            for (var i = e[r] << 16 | e[r + 1] << 8 | e[r + 2], a = 0; a < 4; a++)
                                8 * r + 6 * a <= 8 * e.length ? n.push(t.charAt(i >>> 6 * (3 - a) & 63)) : n.push("=");
                        return n.join("")
                    },
                    base64ToBytes: function (e) {
                        e = e.replace(/[^A-Z0-9+\/]/gi, "");
                        for (var n = [], r = 0, i = 0; r < e.length; i = ++r % 4)
                            0 != i && n.push((t.indexOf(e.charAt(r - 1)) & Math.pow(2, -2 * i + 8) - 1) << 2 * i | t.indexOf(e.charAt(r)) >>> 6 - 2 * i);
                        return n
                    }
                },
                e.exports = n
        }
    ))
        , s = {
        utf8: {
            stringToBytes: function (e) {
                return s.bin.stringToBytes(unescape(encodeURIComponent(e)))
            },
            bytesToString: function (e) {
                return decodeURIComponent(escape(s.bin.bytesToString(e)))
            }
        },
        bin: {
            stringToBytes: function (e) {
                for (var t = [], n = 0; n < e.length; n++)
                    t.push(255 & e.charCodeAt(n));
                return t
            },
            bytesToString: function (e) {
                for (var t = [], n = 0; n < e.length; n++)
                    t.push(String.fromCharCode(e[n]));
                return t.join("")
            }
        }
    }
        , o = s
        , u = function (e) {
        return null != e && (c(e) || function (e) {
            return "function" == typeof e.readFloatLE && "function" == typeof e.slice && c(e.slice(0, 0))
        }(e) || !!e._isBuffer)
    };

    function c(e) {
        return !!e.constructor && "function" == typeof e.constructor.isBuffer && e.constructor.isBuffer(e)
    }

    var l = r((function (e) {
            var t, n, r, i, s;
            t = a,
                n = o.utf8,
                r = u,
                i = o.bin,
                s = function e(a, s) {
                    a.constructor == String ? a = s && "binary" === s.encoding ? i.stringToBytes(a) : n.stringToBytes(a) : r(a) ? a = Array.prototype.slice.call(a, 0) : Array.isArray(a) || a.constructor === Uint8Array || (a = a.toString());
                    for (var o = t.bytesToWords(a), u = 8 * a.length, c = 1732584193, l = -271733879, h = -1732584194, d = 271733878, f = 0; f < o.length; f++)
                        o[f] = 16711935 & (o[f] << 8 | o[f] >>> 24) | 4278255360 & (o[f] << 24 | o[f] >>> 8);
                    o[u >>> 5] |= 128 << u % 32,
                        o[14 + (u + 64 >>> 9 << 4)] = u;
                    var g = e._ff
                        , m = e._gg
                        , p = e._hh
                        , y = e._ii;
                    for (f = 0; f < o.length; f += 16) {
                        var v = c
                            , _ = l
                            , w = h
                            , b = d;
                        c = g(c, l, h, d, o[f + 0], 7, -680876936),
                            d = g(d, c, l, h, o[f + 1], 12, -389564586),
                            h = g(h, d, c, l, o[f + 2], 17, 606105819),
                            l = g(l, h, d, c, o[f + 3], 22, -1044525330),
                            c = g(c, l, h, d, o[f + 4], 7, -176418897),
                            d = g(d, c, l, h, o[f + 5], 12, 1200080426),
                            h = g(h, d, c, l, o[f + 6], 17, -1473231341),
                            l = g(l, h, d, c, o[f + 7], 22, -45705983),
                            c = g(c, l, h, d, o[f + 8], 7, 1770035416),
                            d = g(d, c, l, h, o[f + 9], 12, -1958414417),
                            h = g(h, d, c, l, o[f + 10], 17, -42063),
                            l = g(l, h, d, c, o[f + 11], 22, -1990404162),
                            c = g(c, l, h, d, o[f + 12], 7, 1804603682),
                            d = g(d, c, l, h, o[f + 13], 12, -40341101),
                            h = g(h, d, c, l, o[f + 14], 17, -1502002290),
                            c = m(c, l = g(l, h, d, c, o[f + 15], 22, 1236535329), h, d, o[f + 1], 5, -165796510),
                            d = m(d, c, l, h, o[f + 6], 9, -1069501632),
                            h = m(h, d, c, l, o[f + 11], 14, 643717713),
                            l = m(l, h, d, c, o[f + 0], 20, -373897302),
                            c = m(c, l, h, d, o[f + 5], 5, -701558691),
                            d = m(d, c, l, h, o[f + 10], 9, 38016083),
                            h = m(h, d, c, l, o[f + 15], 14, -660478335),
                            l = m(l, h, d, c, o[f + 4], 20, -405537848),
                            c = m(c, l, h, d, o[f + 9], 5, 568446438),
                            d = m(d, c, l, h, o[f + 14], 9, -1019803690),
                            h = m(h, d, c, l, o[f + 3], 14, -187363961),
                            l = m(l, h, d, c, o[f + 8], 20, 1163531501),
                            c = m(c, l, h, d, o[f + 13], 5, -1444681467),
                            d = m(d, c, l, h, o[f + 2], 9, -51403784),
                            h = m(h, d, c, l, o[f + 7], 14, 1735328473),
                            c = p(c, l = m(l, h, d, c, o[f + 12], 20, -1926607734), h, d, o[f + 5], 4, -378558),
                            d = p(d, c, l, h, o[f + 8], 11, -2022574463),
                            h = p(h, d, c, l, o[f + 11], 16, 1839030562),
                            l = p(l, h, d, c, o[f + 14], 23, -35309556),
                            c = p(c, l, h, d, o[f + 1], 4, -1530992060),
                            d = p(d, c, l, h, o[f + 4], 11, 1272893353),
                            h = p(h, d, c, l, o[f + 7], 16, -155497632),
                            l = p(l, h, d, c, o[f + 10], 23, -1094730640),
                            c = p(c, l, h, d, o[f + 13], 4, 681279174),
                            d = p(d, c, l, h, o[f + 0], 11, -358537222),
                            h = p(h, d, c, l, o[f + 3], 16, -722521979),
                            l = p(l, h, d, c, o[f + 6], 23, 76029189),
                            c = p(c, l, h, d, o[f + 9], 4, -640364487),
                            d = p(d, c, l, h, o[f + 12], 11, -421815835),
                            h = p(h, d, c, l, o[f + 15], 16, 530742520),
                            c = y(c, l = p(l, h, d, c, o[f + 2], 23, -995338651), h, d, o[f + 0], 6, -198630844),
                            d = y(d, c, l, h, o[f + 7], 10, 1126891415),
                            h = y(h, d, c, l, o[f + 14], 15, -1416354905),
                            l = y(l, h, d, c, o[f + 5], 21, -57434055),
                            c = y(c, l, h, d, o[f + 12], 6, 1700485571),
                            d = y(d, c, l, h, o[f + 3], 10, -1894986606),
                            h = y(h, d, c, l, o[f + 10], 15, -1051523),
                            l = y(l, h, d, c, o[f + 1], 21, -2054922799),
                            c = y(c, l, h, d, o[f + 8], 6, 1873313359),
                            d = y(d, c, l, h, o[f + 15], 10, -30611744),
                            h = y(h, d, c, l, o[f + 6], 15, -1560198380),
                            l = y(l, h, d, c, o[f + 13], 21, 1309151649),
                            c = y(c, l, h, d, o[f + 4], 6, -145523070),
                            d = y(d, c, l, h, o[f + 11], 10, -1120210379),
                            h = y(h, d, c, l, o[f + 2], 15, 718787259),
                            l = y(l, h, d, c, o[f + 9], 21, -343485551),
                            c = c + v >>> 0,
                            l = l + _ >>> 0,
                            h = h + w >>> 0,
                            d = d + b >>> 0
                    }
                    return t.endian([c, l, h, d])
                }
                ,
                s._ff = function (e, t, n, r, i, a, s) {
                    var o = e + (t & n | ~t & r) + (i >>> 0) + s;
                    return (o << a | o >>> 32 - a) + t
                }
                ,
                s._gg = function (e, t, n, r, i, a, s) {
                    var o = e + (t & r | n & ~r) + (i >>> 0) + s;
                    return (o << a | o >>> 32 - a) + t
                }
                ,
                s._hh = function (e, t, n, r, i, a, s) {
                    var o = e + (t ^ n ^ r) + (i >>> 0) + s;
                    return (o << a | o >>> 32 - a) + t
                }
                ,
                s._ii = function (e, t, n, r, i, a, s) {
                    var o = e + (n ^ (t | ~r)) + (i >>> 0) + s;
                    return (o << a | o >>> 32 - a) + t
                }
                ,
                s._blocksize = 16,
                s._digestsize = 16,
                e.exports = function (e, n) {
                    if (null == e)
                        throw new Error("Illegal argument " + e);
                    var r = t.wordsToBytes(s(e, n));
                    return n && n.asBytes ? r : n && n.asString ? i.bytesToString(r) : t.bytesToHex(r)
                }
        }
    ));

    function h() {
        var e = function () {
            return Math.floor(65536 * (1 + Math.random())).toString(16).substring(1)
        };
        return e() + e() + "-" + e() + "-" + e() + "-" + e() + "-" + (e() + e() + e())
    }

    function d(e) {
        return new Promise((function (t) {
                var n, r = document.createElement("script"), i = document.getElementsByTagName("head")[0];
                r.src = e,
                    r.onload = r.onreadystatechange = function () {
                        n || r.readyState && !/loaded|complete/.test(r.readyState) || (r.onload = r.onreadystatechange = null,
                            t(n = !0))
                    }
                    ,
                    i.appendChild(r)
            }
        ))
    }

    function f(e, t, n) {
        if (void 0 === t && (t = !1),
        void 0 === n && (n = "048a9c4943398714b356a696503d2d36"),
        "string" == typeof t && "boolean" == typeof n) {
            var r = t;
            t = n,
                n = r
        }
        t && console.log("转化前params=", e);
        var i = function (e, t) {
            return null === t ? void 0 : t
        }
            , a = Object.keys(e).sort().reduce((function (t, n) {
                return void 0 === e[n] ? t : t + n + function (e) {
                    if ([void 0, null, ""].includes(e))
                        return "";
                    if ("[object Object]" === Object.prototype.toString.call(e))
                        return JSON.stringify(e, i);
                    if (Array.isArray(e)) {
                        var t = "";
                        return e.forEach((function (n, r) {
                                "[object Object]" === Object.prototype.toString.call(n) ? t += JSON.stringify(n, i) : [void 0, null].includes(n) ? t += null : t += n.toString(),
                                r < e.length - 1 && (t += ",")
                            }
                        )),
                            t
                    }
                    return e.toString()
                }(e[n])
            }
        ), "");
        return t && (console.log("转化后paramsToken=", a),
            console.log("salt=", n)),
        /[\u00A0\u3000]/g.test(a) && console.warn("验签警告：请先去除非法字符\\u00A0，\\u3000"),
            l(a += n)
    }

    window._Sign = f;
}]);

function get_sign(time, encrypt_password, mobile, shumeiId) {
    /**
     *
     * @type {{password, countryCode: string, invokeTime: number, browserVersion: string, mobile, shumeiId, browserName: string, ua: string, scene: string}}
     */
    P = {
        "countryCode": "86",
        "mobile": mobile,
        "password": encrypt_password, // password
        "scene": "nc_login",
        "invokeTime": time,
        "shumeiId": shumeiId, // shumeiId
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "browserName": "Chrome",
        "browserVersion": "131.0.0.0"
    }
    sign = window._Sign(P);
    return sign;
}

function biz_sign(obj_params) {
    sign = window._Sign(obj_params);
    return sign;
}
// console.log(biz_sign({
//     'params': {
//         'timeType': 130,
//         //'startTime': None,
//         //'endTime': None,
//     }
// }))
console.log(biz_sign({
    'scene': 6,
    'bizArea': 'gravity',
    'exportToken': '2q6osibYkQ8lI7xFrsSVzaDTe7L',
}
))
