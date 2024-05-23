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

function AEToolXBlockStudio(runtime, element) {
  "use strict";
  
  var fields = [];
  var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
  var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

  $(element).find('.field-data-control').each(function() {
      var $field = $(this);
      var $wrapper = $field.closest('li');
      var $resetButton = $wrapper.find('button.setting-clear');
      var type = $wrapper.data('cast');
      fields.push({
          name: $wrapper.data('field-name'),
          isSet: function() { return $wrapper.hasClass('is-set'); },
          hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
          val: function() {
              var val = $field.val();
              // Cast values to the appropriate type so that we send nice clean JSON over the wire:
              if (type == 'boolean')
                  return (val == 'true' || val == '1');
              if (type == "integer")
                  return parseInt(val, 10);
              if (type == "float")
                  return parseFloat(val);
              if (type == "generic" || type == "list" || type == "set") {
                  val = val.trim();
                  if (val === "")
                      val = null;
                  else
                      val = JSON.parse(val); // TODO: handle parse errors
              }
              return val;
          },
          removeEditor: function() {
              $field.tinymce().remove();
          }
      });
      var fieldChanged = function() {
          // Field value has been modified:
          $wrapper.addClass('is-set');
          $resetButton.removeClass('inactive').addClass('active');
      };
      $field.bind("change input paste", fieldChanged);
      $resetButton.click(function() {
          $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
          $wrapper.removeClass('is-set');
          $resetButton.removeClass('active').addClass('inactive');
      });
      if (type == 'html' && tinyMceAvailable) {
          tinyMCE.baseURL = baseUrl + "/js/vendor/tinymce/js/tinymce";
          $field.tinymce({
              theme: 'silver',
              skin: 'studio-tmce5',
              content_css: 'studio-tmce5',
              height: '200px',
              formats: { code: { inline: 'code' } },
              codemirror: { path: "" + baseUrl + "/js/vendor" },
              convert_urls: false,
              plugins: "lists, link, codemirror",
              menubar: false,
              statusbar: false,
              toolbar_items_size: 'small',
              toolbar: "formatselect | styleselect | bold italic underline forecolor | bullist numlist outdent indent blockquote | link unlink | code",
              resize: "both",
              extended_valid_elements : 'i[class],span[class]',
              setup : function(ed) {
                  ed.on('change', fieldChanged);
              }
          });
      }

      if (type == 'datepicker' && datepickerAvailable) {
          $field.datepicker('destroy');
          $field.datepicker({dateFormat: "m/d/yy"});
      }
  });

  $(element).find('.wrapper-list-settings .list-set').each(function() {
      var $optionList = $(this);
      var $checkboxes = $(this).find('input');
      var $wrapper = $optionList.closest('li');
      var $resetButton = $wrapper.find('button.setting-clear');

      fields.push({
          name: $wrapper.data('field-name'),
          isSet: function() { return $wrapper.hasClass('is-set'); },
          hasEditor: function() { return false; },
          val: function() {
              var val = [];
              $checkboxes.each(function() {
                  if ($(this).is(':checked')) {
                      val.push(JSON.parse($(this).val()));
                  }
              });
              return val;
          }
      });
      var fieldChanged = function() {
          // Field value has been modified:
          $wrapper.addClass('is-set');
          $resetButton.removeClass('inactive').addClass('active');
      };
      $checkboxes.bind("change input", fieldChanged);

      $resetButton.click(function() {
          var defaults = JSON.parse($wrapper.attr('data-default'));
          $checkboxes.each(function() {
              var val = JSON.parse($(this).val());
              $(this).prop('checked', defaults.indexOf(val) > -1);
          });
          $wrapper.removeClass('is-set');
          $resetButton.removeClass('active').addClass('inactive');
      });
  });

  var studio_submit = function(data) {
      var handlerUrl = runtime.handlerUrl(element, 'submit_studio_edits');
      runtime.notify('save', {state: 'start', message: "Saving"});
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify(data),
          dataType: "json",
          global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
          success: function(response) { runtime.notify('save', {state: 'end'}); }
      }).fail(function(jqXHR) {
          var message = "This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.";
          if (jqXHR.responseText) { // Is there a more specific error message we can show?
              try {
                  message = JSON.parse(jqXHR.responseText).error;
                  if (typeof message === "object" && message.messages) {
                      // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                      message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                  }
              } catch (error) { message = jqXHR.responseText.substr(0, 300); }
          }
          runtime.notify('error', {title: "Unable to update settings", message: message});
      });
  };

  $('.save-button', element).bind('click', function(e) {
      e.preventDefault();
      var values = {};
      var notSet = []; // List of field names that should be set to default values
      for (var i in fields) {
          var field = fields[i];
          if (field.isSet()) {
              values[field.name] = field.val();
          } else {
              notSet.push(field.name);
          }
          // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
          // when loading editor for another block:
          if (field.hasEditor()) {
              field.removeEditor();
          }
      }
      const aetoolEle = $(element).find('#xb-field-edit-aetool');
      const $aetool = $(aetoolEle);
      if ($aetool.val() === 'iframe') {
        values['iframe_url'] = values['aetool_config']['iframe_url']
      } else if ($aetool.val() === 'simulator') {
        values['iframe_url'] = 'https://ae-custom-question.learning.app.meca.in.th/simulator'
      } else if ($aetool.val() === 'chatbot') {
        values['iframe_url'] = 'https://abdul.in.th/chat/adaptive/?msg=แบบทดสอบกิจกรรมที่ 1'
      } else if ($aetool.val() === 'bookroll') {
        values['iframe_url'] = 'https://ae-ui.pages.dev/pdf.html'
      }
      // console.log(values)
      studio_submit({values: values, defaults: notSet});
  });

  $(element).find('.cancel-button').bind('click', function(e) {
      // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
      // when loading editor for another block:
      for (var i in fields) {
          var field = fields[i];
          if (field.hasEditor()) {
              field.removeEditor();
          }
      }
      e.preventDefault();
      runtime.notify('cancel', {});
  });


  const aetoolEle = $(element).find('#xb-field-edit-aetool');
  const aetoolConfigEle = $(element).find(`.field-aetool-config-control`);
  const aetoolFieldEles = $(element).find(`.aetool-config-field`);
  aetoolEle.on('change', function() {
    const aetoolFieldEle = $(element).find('#xb-field-edit-aetool_config');
    for (const f of aetoolFieldEles) {
      const ff = $(f)
      if (this.value === ff.data('aetool-config-name')) {
        ff.show()
      } else {
        ff.hide()
      }
    }
    aetoolFieldEle.val('{}');
  });
  
  aetoolConfigEle.on('change', function () {
    const aetoolFieldEle = $(element).find('#xb-field-edit-aetool_config');
    var $wrapper = $(aetoolFieldEle).closest('li');
    const d = JSON.parse(aetoolFieldEle.val());
    if ($(this).data('aetool-config-name') === aetoolEle.val()) {
      d[$(this).data('aetool-config-field-name')] = $(this).val()
    } else {
      d[$(this).data('aetool-config-field-name')] = null
    }
    aetoolFieldEle.val(JSON.stringify(d));
    $wrapper.addClass('is-set');
  });
  for (const f of aetoolFieldEles) {
    const ff = $(f)
    if (aetoolEle.val() === ff.data('aetool-config-name')) {
      ff.show()
    } else {
      ff.hide()
    }
  }
  $(element).find(`[data-field-name='iframe_url']`).each(function () {
    $(this).hide()
  })
}
