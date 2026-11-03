var rule = {
    title:'51麻豆',
    host:'https://51md.me',
    url:'/vod-show/id/fyclass/page/fypage',
    class_name:'麻豆原创&天美&蜜桃&91&精东&海角&杏吧&糖心',
    class_url:'1&2&3&4&5&6&7&8',
    headers:{'User-Agent':'Mozilla/5.0','Referer':'https://51md.me'},
    推荐:'ul.vod-list li;a&&title;a&&href;img&&data-original;.text&&Text',
    一级:'ul.vod-list li;a&&title;a&&href;img&&data-original;.text&&Text',
    二级:{
        title:'h1&&Text',
        img:'.vod-img img&&data-original',
        desc:';.info li&&Text',
        content:'.content&&Text',
        tabs:'js:tabs = [];pdfa(html,".playlist a").forEach(a=>{tabs.push(pdfh(a,"a&&Text"))});VOD.vod_play_from=tabs.join("$$$")',
        lists:'.playlist:eq(#id) li;a&&Text;a&&href',
    },
    搜索:'ul.vod-list li;a&&title;a&&href;img&&data-original;.text&&Text',
    搜索url:'/vod-search/wd/{wd}/page/{pg}',
    searchable:2,
    quickSearch:1,
    filterable:0,
    lazy:$js.toString(()=>{
        let html = request(input);
        let m = html.match(/"url"\s*:\s*"(https[^"]+\.m3u8)"/);
        if(m) input = m[1].replace(/\\/g,'');
        else {
           let iframe = pdfh(html,'iframe&&src');
           if(iframe){
             let h2 = request(iframe);
             let m2 = h2.match(/https?:\/\/[^"']+\.m3u8/);
             if(m2) input = m2[0];
           }
        }
        input = {parse:0,url:input}
    })
}
