/* Javascript for AEToolXBlock. */
function AEToolXBlock(runtime, element) {
    function createIframeElelment(wrapper) {
      const username = wrapper.data('user-name');
      const userrole = wrapper.data('user-role');
      const params = [
        `userName=${username}`,
        `userRole=${userrole}`,
        `definitionId=${encodeURIComponent(wrapper.data('definition-id'))}`,
        `usageId=${encodeURIComponent(wrapper.data('usage-id'))}`,
        `view=${wrapper.data('view')}`,
      ]
      const iframe = $('<iframe>').attr({
        title: wrapper.data('title'),
        name: `iframe-${wrapper.data('target')}`,
        id: `iframe-${wrapper.data('target')}`,
        src: `${wrapper.data('iframe-url')}?${params.join('&')}` ,
        allowfullscreen: "true",
        webkitallowfullscreen: "true",
        mozallowfullscreen: "true",
        allow: "microphone *; camera *; midi *; geolocation *; encrypted-media *"
      }).css({
        width: wrapper.data('width') || '100%',
        height: wrapper.data('height') || '100%'
      });
      iframe.on('message', console.log);
      return iframe;
    }
  
    function handleOpenModalButtonClick(eventObject) {
      const wrapper = $(eventObject.target).parent();
      if (window !== window.parent) {
        // window.parent.addEventListener('message', console.log)
        const username = wrapper.data('user-name');
        const userrole = wrapper.data('user-role');
        const params = [
          `userName=${username}`,
          `userRole=${userrole}`,
          `definitionId=${encodeURIComponent(wrapper.data('definition-id'))}`,
          `usageId=${encodeURIComponent(wrapper.data('usage-id'))}`,
          `view=${wrapper.data('view')}`
        ]
        window.parent.postMessage(
            {
                'type': 'plugin.modal',
                'payload': {
                    'url': `${wrapper.data('iframe-url')}?${params.join('&')}`,
                    'title': wrapper.data('title'),
                    'width': wrapper.data('width')
                }
            },
            document.referrer
        );
        return;
      }
      const innerWrapper = $('<div>');
      innerWrapper.addClass('inner-wrapper');
      innerWrapper.attr('role', 'dialog');
      innerWrapper.css({height: '100%', padding: '0 0 0 0'});
      let closeButton = $('<button>');
      closeButton.addClass('close-modal');
      closeButton.append('<i class="icon fa fa-remove"></i>');
      closeButton.append('<span class="sr">Close</span>');
      let modal = $('<section>');
      modal.addClass('modal');
      modal.attr('aria-hidden', 'true');
      modal.css({width: wrapper.data('width'), left: '10%', top: '10%', bottom: '10%', opacity: 1, zIndex: 11000, position: 'fixed', display: 'block'});
      const defaults = { top: 100, overlay: 0.5, closeButton: null };
      const overlay_id = 'lean_overlay';
      const iframe = createIframeElelment(wrapper)
      innerWrapper.append(closeButton);
      innerWrapper.append(iframe);
      modal.append(innerWrapper);
      wrapper.append(modal);
      $("#" + overlay_id).click(function () {
          close_modal(modal)
      });
      closeButton.click(function () {
        close_modal(modal)
      })
      $("#" + overlay_id).css({ "display": "block", opacity: 0 });
      $("#" + overlay_id).fadeTo(200, 0.5);
      modal.fadeTo(200, 1);
      modal.attr('aria-hidden', false);
      $('body').css('overflow', 'hidden');
  
      eventObject.preventDefault();
  
      /* Manage focus for modal dialog */
      /* Set focus on close button */
      closeButton.focus();
  
      /* Redirect close button to iframe */
      closeButton.on('keydown', function (e) {
          if (e.which === 9) {
              e.preventDefault();
              // This is a workaround due to Firefox triggering focus calls oddly.
              setTimeout(function () {
                  modal.find('iframe')[0].contentWindow.focus();
              }, 1);
          }
      });
      document.addEventListener('keydown', (event) => {
        if (event.code === 'Escape') {
          close_modal(modal)
        }
      });
    }
  
    function handleOpenNewWindowButtonClick(eventObject) {
      const wrapper = $(eventObject.target.parent);
      const newWindow = window.open(wrapper.data('iframe-url'));
      newWindow.addEventListener('message', console.log);
    }
  
    function close_modal(modal) {
      $('select, input, textarea, button, a').off('focus');
      const overlay_id = 'lean_overlay';
      $("#" + overlay_id).fadeOut(200);
      $("#" + overlay_id).css({ "display": "none" });
      modal.css({ "display": "none" });
      modal.attr('aria-hidden', true);
      modal.find('iframe').attr('src', '');
      $('body').css('overflow', 'auto');
    }
  
      $(function ($) {
        const wrapper = $(element).find('.wrapper');
        if (wrapper.data('display') === 'inline') {
          wrapper.append(createIframeElelment(wrapper));
        } else if (wrapper.data('display') === 'modal') {
          const button = $('<button>');
          button.addClass("btn btn-pl-primary btn-base");
          button.text(wrapper.data('btn-text'));
          button.click(handleOpenModalButtonClick);
          wrapper.append(button);
        } else if (wrapper.data('display') === 'modalWithInline') {
          wrapper.append(createIframeElelment(wrapper));
        } else if (wrapper.data('display') === 'newWindow') {
          const button = $('<button>');
          button.addClass("btn btn-pl-primary btn-base");
          button.text(wrapper.data('btn-text'));
          button.click(handleOpenNewWindowButtonClick);
          wrapper.append(button);
        }
      });
  }
