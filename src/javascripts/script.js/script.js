// O QUE FAZ: inicia os comportamentos da página quando o DOM termina de carregar.
// ONDE APARECE: lógica global da navegação.
// QUANDO ATUA: no carregamento da página.
$(document).ready(function () {
    // O QUE FAZ: abre/fecha menu mobile e alterna ícone do botão.
    // ONDE APARECE: botão #mobile_btn e bloco #mobile_menu.
    // QUANDO ATUA: ao clicar no botão hambúrguer.
    $('#mobile_btn').on('click', function () {
        $('#mobile_menu').toggleClass('active');
        $('#mobile_btn').find('i').toggleClass('fa-x');
    });

    const sections = $('section');
    const navitens = $('.navitem');

    $(window).on('scroll', function(){
        
        const header = $('header');
        const scrollPosition = $(window).scrolTop() - header.outerHeight();
        let activeSectionIndex = 0;

        if (scrollPosition <= 0){
            header.css('box-shadow', 'none')

        } else {
            header.css('box-shadow', '5px 1px 5px rgba(0, 0, 0, 0.1,');
        }

        sections.each(function(i){
            const section = $(this);
            const sectionTop = section.offset().top - 96;
            const sectionBottom = sectionTop+section.outerHeight();

            if(scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeSectionIndex = i;
                return false;
            }
        })

        navitens.removeClass('active');
        $(navitens[activeSectionIndex]).addClass('active');
    });

    scrollReveal().reveal('#cta', {
        origin: 'left',
        duration: 2000,
        distance: '20%',
    });

    scrollReveal().reveal('.dish', {
        origin: 'left',
        duration: 2000,
        distance: '20%',
    });

    scrollReveal().reveal('.testimonials_Chef', {
        origin: 'left',
        duration: 2000,
        distance: '20%',
    })

    // O QUE FAZ: atualiza item ativo da navegação e fecha menu mobile.
    // ONDE APARECE: links da navbar desktop e mobile.
    // QUANDO ATUA: ao clicar em qualquer link de navegação.
    $('#nav_list .nav-item a, #mobile_nav_list .nav-item a').on('click', function () {
        const alvo = $(this).attr('href');

        $('#nav_list .nav-item, #mobile_nav_list .nav-item').removeClass('active');
        $(`#nav_list .nav-item a[href="${alvo}"]`).parent().addClass('active');
        $(`#mobile_nav_list .nav-item a[href="${alvo}"]`).parent().addClass('active');

        $('#mobile_menu').removeClass('active');
    });
});