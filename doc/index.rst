====================
Python libremarkable
====================

.. automodule:: libremarkable
   :members:

   .. class:: Keymap

      alias of :py:class:`dict` [ :py:class:`tuple` [ :py:class:`str` | :py:data:`None`, :py:class:`str` | :py:data:`None` ]]

   .. data:: deviceType
      :type: DeviceType

      Current device type

   .. data:: DEFAULT_FONT_SIZE
      :annotation: = 24
      :type: int

      The default font size

   .. data:: DEFAULT_KEYMAP
      :type: Keymap

      The default keymap

   .. data:: Framebuffer
      :type: libremarkable._framebuffer.FrameBuffer

      Framebuffer API instance

   .. autoclass:: libremarkable._framebuffer.FrameBuffer
      :members:
      :show-inheritance:

.. automodule:: libremarkable.geometry
   :members:
