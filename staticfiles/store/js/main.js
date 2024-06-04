// Função para ordenar produtos por maior-preco, menor-preco e mais-vendidos

var url = new URL(document.URL);
var itens = document.getElementsByClassName("ordenar-produtos");
for (i = 0; i < itens.length; i++){
    url.searchParams.set("ordem", itens[i].value);
    itens[i].value = url.href;
}
